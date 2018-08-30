from UI import ui_manager as ui
from TestingSuite import test
from EmailManager import email_manager
from DatabaseManager import db_manager

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
    db_manager.write_file_data("non_static\\portfolio_report.txt", "\n".join(report_data))

    time.sleep(1)
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "color": ui.GREEN,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database...",
                                                                       "   Written."],
                                                           "lifespan": 3})
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
