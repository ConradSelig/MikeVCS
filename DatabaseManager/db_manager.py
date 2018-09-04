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
    report_data.append("Current Value: " + format(portfolio_data[-1][1], ".4f"))
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
            try:
                file.write(str(event))
            except MemoryError:
                ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.RED,
                                                                         "TextBox": ["Reading in known events...",
                                                                                     "   Compiled "
                                                                                     "(" + str(
                                                                                         len(existing_events)) + ")",
                                                                                     "Adding new Events...",
                                                                                     "   FAILED (MemoryError)"],
                                                                         "lifespan": 15})
                return

    added_events = 0
    for event in new_events:
        if str(event) not in existing_events:
            try:
                file.write(str(event) + "\n")
            except MemoryError:
                ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.RED,
                                                                         "TextBox": ["Reading in known events...",
                                                                                     "   Compiled "
                                                                                     "(" + str(
                                                                                         len(existing_events)) + ")",
                                                                                     "Adding new Events...",
                                                                                     "   FAILED (MemoryError)"],
                                                                         "lifespan": 15})
                return
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


def check_database():
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Database Check",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Looking for errors..."]})

    metadata_files = os.listdir(DATABASE_PATH + "contact_metadata\\")
    user_files = os.listdir(DATABASE_PATH + "user_data\\")
    time.sleep(1)

    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users."],
                                                          "color": ui.YELLOW if len(metadata_files) == len(user_files)
                                                          else ui.RED})

    time.sleep(0.5)

    if len(metadata_files) != len(user_files):

        ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                          "   " + str(
                                                                              len(metadata_files)) + " metadata.",
                                                                          "   " + str(len(user_files)) + " users.",
                                                                          "Repairing..."]})

        if len(metadata_files) < len(user_files):
            for user_file in user_files:
                if user_file not in metadata_files:
                    os.mkdir(DATABASE_PATH + "contact_metadata\\" + user_file)
                    open(DATABASE_PATH + "contact_metadata\\" + user_file + "\\metadata.txt", "w").close()
        elif len(user_files) < len(metadata_files):
            for metadata_file in user_files:
                if metadata_file not in user_files:
                    os.mkdir(DATABASE_PATH + "user_data\\" + metadata_file)
                    open(DATABASE_PATH + "user_data\\" + metadata_file + "\\habits.txt", "w").close()
                    open(DATABASE_PATH + "user_data\\" + metadata_file + "\\metadata.txt", "w").close()

    metadata_files = os.listdir(DATABASE_PATH + "contact_metadata\\")
    user_files = os.listdir(DATABASE_PATH + "user_data\\")
    time.sleep(0.5)

    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files..."],
                                                          "color": ui.YELLOW if len(metadata_files) == len(user_files)
                                                          else ui.RED})

    file_errors = 0

    for user_file in user_files:
        try:
            open(DATABASE_PATH + "user_data\\" + user_file + "\\habits.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\habits.txt", "w").close()
        try:
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "w").close()
    for metadata_file in metadata_files:
        try:
            open(DATABASE_PATH + "contact_metadata\\" + metadata_file + "\\metadata.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "w").close()
    time.sleep(1)

    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files...",
                                                                      "   Complete",
                                                                      "   (" + str(file_errors) + " repairs made)"],
                                                          "color": ui.YELLOW})

    time.sleep(1)
    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files...",
                                                                      "   Complete",
                                                                      "   (" + str(file_errors) + " repairs made)",
                                                                      "",
                                                                      "Check complete!"],
                                                          "color": ui.GREEN,
                                                          "lifespan": 3})

    return
