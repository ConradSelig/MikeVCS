from UI import ui_manager as ui
from TestingSuite import test
from EmailManager import email_manager
from ScheduleManager import schedule_manager
from DatabaseManager import db_manager

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

    while running:
        tick_count += 1
        time.sleep(0.01)

        new_emails = email_manager.get_email_stack()
        db_manager.update_db()

        # print(running)
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
