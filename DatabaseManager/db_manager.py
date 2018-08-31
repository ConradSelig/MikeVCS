from UI import ui_manager as ui

from math import floor, log10
from datetime import datetime
import time
import os
import re

from Robinhood import Robinhood

DATABASE_PATH = re.search("(.*)\\\\.*", os.path.realpath(__file__)).group(1) + "\\Database\\"


def build_portfolio_report():
    this_id = str(datetime.now())
    ui.DisplayQueueManager.request_connection(["Main", "Database"], {"title": "Stock Portfolio",
                                                                     "color": ui.YELLOW,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Building end of day report..."]})

    portfolio_data = get_file_data("non_static\\stock_portfolio.txt")
    report_data = []
    for index, line in enumerate(portfolio_data):
        portfolio_data[index] = portfolio_data[index].split("; ")
        portfolio_data[index][1] = float(portfolio_data[index][1].replace("\n", ""))
    days_change = round(portfolio_data[-1][1] - portfolio_data[0][1], 4)
    days_percent_change = days_change / portfolio_data[0][1]

    current_date = str(datetime.now().date()).split("-")
    report_data.append("Portfolio Report for: " + current_date[1] + "/" + current_date[2] + "/" + current_date[0])
    if days_change == 0:
        report_data.append("Portfolio's value did not change for the day")
    elif days_change > 0:
        report_data.append("Value Gained over day: $" + format(days_change, ".4f"))
        report_data.append("Percent Increased over day: " +
                           str(round(days_percent_change, -int(floor(log10(abs(days_percent_change)))))) + "%")
    else:
        report_data.append("Value Lost over day: $" + format(days_change, ".4f"))
        report_data.append("Percent Decreased over day: " +
                           str(round(days_percent_change, -int(floor(log10(abs(days_percent_change)))))) + "%")

    robin_trader = Robinhood()
    robin_trader.login("ConradSelig", open(DATABASE_PATH + "static\\pass.txt", "r").read())

    dsecowned = robin_trader.securities_owned()["results"]
    report_data.append("\nStocks Owned: ")
    for position in dsecowned:
        id = position['instrument'].split('/')[4]
        if float(position['quantity']) > 0:
            report_data.append("   Stock Name: " + robin_trader.instrument(id)['name'])
            report_data.append("   Stock Symbol: " + robin_trader.instrument(id)['symbol'])
            num_owned = position['quantity']
            report_data.append("      Number Owned: " + num_owned)
            value_per = robin_trader.bid_price(robin_trader.instrument(id)['symbol'])[0][0]
            report_data.append("      Value per Stock: " + format(float(value_per), ".4f"))
            report_data.append("      Portfolio Value: " + format((float(num_owned) * float(value_per)), ".4f"))

    time.sleep(1)
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database..."]})

    write_file_data("non_static\\portfolio_report.txt", "\n".join(report_data))

    time.sleep(1)
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "color": ui.GREEN,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database...",
                                                                       "   Written."],
                                                           "lifespan": 3})

    '''
        Exception in thread Thread-1:
        Traceback (most recent call last):
          File "C:\ Users\Conrad Selig\AppData\Local\Programs\Python\Python36-32\lib\threading.py", line 916, in _bootstrap_inner
            self.run()
          File "C:\ Users\Conrad Selig\AppData\Local\Programs\Python\Python36-32\lib\threading.py", line 864, in run
            self._target(*self._args, **self._kwargs)
          File "C:/Users/Conrad Selig/PycharmProjects/MikeVCS/manage.py", line 50, in main
            db_manager.update_db()
          File "C:\ Users\Conrad Selig\PycharmProjects\MikeVCS\DatabaseManager\db_manager.py", line 27, in update_db
            store_calendar_events(schedule_manager.build_events())
          File "C:\ Users\Conrad Selig\PycharmProjects\MikeVCS\DatabaseManager\db_manager.py", line 86, in store_calendar_events
            file.write(str(event))
        MemoryError
    '''

    return


def update_stock_portfolio_record():

    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "r")
    excising_data = file.readlines()
    file.close()

    this_id = str(datetime.now())

    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Portfolio Record",
                                                             "color": ui.YELLOW,
                                                             "unique_id": this_id,
                                                             "TextBox": ["Number of old records:",
                                                                         "   " + str(len(excising_data)),
                                                                         "",
                                                                         "Adding new record..."]})

    robin_trader = Robinhood()
    robin_trader.login("ConradSelig", open(DATABASE_PATH + "static\\pass.txt", "r").read())
    profile_data = robin_trader.portfolios()

    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "a")
    file.write(str(datetime.now()) + "; " + profile_data["equity"] + "\n")
    file.close()

    ui.DisplayQueueManager.update_data("Updating Portfolio Record", {"color": ui.GREEN,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Number of old records:",
                                                                                 "   " + str(len(excising_data)),
                                                                                 "",
                                                                                 "Adding new record...",
                                                                                 "   Done"],
                                                                     "lifespan": 3})


def store_calendar_events(new_events):
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Calendar",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Reading in known events..."]})

    existing_events = get_file_data("non_static\\calendar_events.txt")
    time.sleep(1)
    ui.DisplayQueueManager.update_data("Updating Calendar", {"TextBox": ["Reading in known events...",
                                                                         "   Compiled "
                                                                         "(" + str(len(existing_events)) + ")",
                                                                         "Adding new Events..."]})
    file = open(DATABASE_PATH + "non_static\\calendar_events.txt", "w")

    for index, event in enumerate(existing_events):
        existing_events[index] = event.replace("\n", "")
        event = parse_calendar_event(event)
        datetime_string = event[0][0] + " " + event[0][1] + " " + event[0][2] + " " + event[1]
        datetime_event = datetime.strptime(datetime_string, "%m %d %Y %H:%M")
        if datetime_event > datetime.now():
            file.write(str(event))
    added_events = 0
    for event in new_events:
        if str(event) not in existing_events:
            file.write(str(event) + "\n")
            added_events += 1

    file.close()
    time.sleep(1)

    ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.GREEN,
                                                             "TextBox": ["Reading in known events...",
                                                                         "   Compiled "
                                                                         "(" + str(len(existing_events)) + ")",
                                                                         "Adding new Events...",
                                                                         "   New Events Added "
                                                                         "(" + str(added_events) + ")"],
                                                             "lifespan": 3})


def parse_calendar_event(event):
    date_re = re.search("^\[\['(..)', '(..)', '(....)']", event)
    date = [date_re.group(1), date_re.group(2), date_re.group(3)]
    time_name_re = re.search(".{24}(..:..)', '(..:..)', '(.*)']$", event)
    event = [date, time_name_re.group(1), time_name_re.group(2), time_name_re.group(3)]
    return event


def get_file_data(file_name, read_lines=True):
    file_name = DATABASE_PATH + file_name
    file = open(file_name, "r")
    if read_lines:
        data = file.readlines()
    else:
        data = file.read()
    file.close()
    return data


def write_file_data(file_name, data, append=False):
    file_name = DATABASE_PATH + file_name
    file = open(file_name, "a" if append else "w")
    file.write(data)
    file.close()
    return
