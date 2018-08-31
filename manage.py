from UI import ui_manager as ui
from TestingSuite import test
from EmailManager import email_manager
from DatabaseManager import db_manager
from Robinhood import Robinhood

from math import floor, log10
from datetime import datetime
import time
import logging
import threading


class DisplayState:

    state = type(bool)

    def __init__(self):
        self.state = True

    def get_state(self):
        return self.state

    def change_state(self, new_state):
        self.state = new_state


CurrentDisplayState = DisplayState()


def setup():
    main_loop = threading.Thread(target=main).start()
    display_exit_thread = threading.Thread(target=wait_for_exit).start()
    ui.main(DisplayState())


def main():

    test.test_display()

    running = True
    tick_count = 0
    last_db_update = ""
    build_report = True

    while running:
        tick_count += 1
        time.sleep(0.01)

        new_emails = email_manager.get_email_stack()
        db_manager.update_db()

        if build_report:
            build_portfolio_report()
            build_report = False

        # print(running)
    return


def build_portfolio_report():
    this_id = str(datetime.now())
    ui.DisplayQueueManager.request_connection(["Main", "Database"], {"title": "Stock Portfolio",
                                                                     "color": ui.YELLOW,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Building end of day report..."]})

    portfolio_data = db_manager.get_file_data("non_static\\stock_portfolio.txt")
    report_data = []
    for index, line in enumerate(portfolio_data):
        portfolio_data[index] = portfolio_data[index].split("; ")
        portfolio_data[index][1] = float(portfolio_data[index][1].replace("\n", ""))
    days_change = round(portfolio_data[-1][1] - portfolio_data[0][1], 4)
    days_percent_change = days_change / portfolio_data[0][1]

    time.sleep(1)
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database..."]})

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
    robin_trader.login("ConradSelig", open(db_manager.DATABASE_PATH + "static\\pass.txt", "r").read())

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
            report_data.append("      Value per Stock: " + value_per)
            report_data.append("      Portfolio Value: " + format((float(num_owned) * float(value_per)), ".4f"))

    db_manager.write_file_data("non_static\\portfolio_report.txt", "\n".join(report_data))

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


def wait_for_exit():
    input("Display Exit Thread Started\n")
    CurrentDisplayState.change_state(False)
    return


def exit_protocol():
    print("Closing")
    ui.close_display()
    exit(0)


if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exit_protocol()
    except (BaseException, Exception):
        print("\n\n")
        logging.exception("A Fatal Error has Occurred")
        print("\n\n")
        exit_protocol()
