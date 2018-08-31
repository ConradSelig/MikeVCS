from UI import ui_manager as ui
from TestingSuite import test
from EmailManager import email_manager
from DatabaseManager import db_manager
from ScheduleManager import schedule_manager

from datetime import datetime

import datetime as dt
import threading
import logging
import time
import ast


class DisplayState:

    state = type(bool)

    def __init__(self):
        self.state = True

    def get_state(self):
        return self.state

    def change_state(self, new_state):
        self.state = new_state


CurrentDisplayState = DisplayState()

LONG_UPDATE = datetime.now() - dt.timedelta(minutes=100)
REG_UPDATE = datetime.now() - dt.timedelta(minutes=100)
SHORT_UPDATE = datetime.now() - dt.timedelta(minutes=100)


def setup():
    main_loop = threading.Thread(target=main).start()
    display_exit_thread = threading.Thread(target=wait_for_exit).start()
    ui.main(DisplayState())


def main():

    test.test_display()

    running = True
    tick_count = 0

    while running:
        tick_count += 1
        time.sleep(0.01)

        new_emails = email_manager.get_email_stack()
        update_db()
        db_manager.write_file_data("non_static\\timers.txt",
                                   str(60 - (datetime.now() - SHORT_UPDATE).seconds) + "\n" +
                                   str(900 - (datetime.now() - REG_UPDATE).seconds) + "\n" +
                                   str(3600 - (datetime.now() - LONG_UPDATE).seconds))

        # print(running)
    return


def update_db():

    global LONG_UPDATE
    global REG_UPDATE
    global SHORT_UPDATE

    trackers_data = ast.literal_eval(
        db_manager.get_file_data("non_static\\trackers.txt", read_lines=False).replace("\n", ""))

    if trackers_data["last_reset_date"] != str(datetime.now().date()):
        trackers_data["do_daily_report"] = True
        trackers_data["last_reset_date"] = str(datetime.now().date())
        db_manager.write_file_data("non_static\\trackers.txt", str(trackers_data))

    if datetime.now() > datetime.strptime("10:00", "%H:%M"):
        trackers_data = ast.literal_eval(
                        db_manager.get_file_data("non_static\\trackers.txt", read_lines=False).replace("\n", ""))
        if trackers_data["do_daily_report"]:
            db_manager.build_portfolio_report()
            trackers_data["do_daily_report"] = False
            db_manager.write_file_data("non_static\\trackers.txt", str(trackers_data))

    if datetime.now() > LONG_UPDATE + dt.timedelta(minutes=60):
        LONG_UPDATE = datetime.now()

    if datetime.now() > REG_UPDATE + dt.timedelta(minutes=15):
        REG_UPDATE = datetime.now()
        db_manager.store_calendar_events(schedule_manager.build_events())

    if datetime.now() > SHORT_UPDATE + dt.timedelta(minutes=1):
        SHORT_UPDATE = datetime.now()
        if datetime(datetime.now().year, datetime.now().month, datetime.now().day) + dt.timedelta(minutes=990) > \
           datetime.now() > \
           datetime(datetime.now().year, datetime.now().month, datetime.now().day) + dt.timedelta(minutes=450):
            db_manager.update_stock_portfolio_record()


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
