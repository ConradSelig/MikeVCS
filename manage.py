from UI import ui_manager as ui
from TestingSuite import test
from EmailManager import email_manager

import time
import logging
import datetime
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


def main():

    test.test_display()

    running = True
    tick_count = 0
    display_thread = threading.Thread(target=show_display)
    display_exit_thread = threading.Thread(target=wait_for_exit)
    display_thread.start()
    display_exit_thread.start()
    while running:
        tick_count += 1
        time.sleep(0.01)

        new_emails = email_manager.get_email_stack()

        # print(running)
    return


def wait_for_exit():
    input("Display Exit Thread Started\n")
    CurrentDisplayState.change_state(False)
    return


def show_display():  # thread
    ui.main(CurrentDisplayState)


def exit_protocol():
    print("Closing")
    ui.close_display()
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exit_protocol()
    except (BaseException, Exception):
        print("\n\n")
        logging.exception("A Fatal Error has Occurred")
        print("\n\n")
        exit_protocol()
