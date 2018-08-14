from UI import ui_manager

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


DisplayQueueManager = ui_manager.QueueHandler()
CurrentDisplayState = DisplayState()


def main():

    DisplayQueueManager.request_connection(["Main"], {"color": ui_manager.GREEN, "title": "tester_A",
                                                      "TextBox": ["Hello", "World"]})
    DisplayQueueManager.request_connection(["AI"], {"color": ui_manager.GREEN, "title": "tester_B"})
    DisplayQueueManager.request_connection(["Database"], {"color": ui_manager.GREEN, "title": "tester_C"})
    DisplayQueueManager.request_connection(["Display"], {"color": ui_manager.RED, "title": "tester_D"})
    DisplayQueueManager.request_connection(["Habit"], {"color": ui_manager.RED, "title": "tester_E"})
    DisplayQueueManager.request_connection(["Email"], {"color": ui_manager.RED, "title": "tester_F",
                                                       "TextBox": ["World", "Hello"]})

    running = True
    tick_count = 0
    display_thread = threading.Thread(target=show_display)
    display_exit_thread = threading.Thread(target=wait_for_exit)
    display_thread.start()
    display_exit_thread.start()
    while running:
        tick_count += 1
        if tick_count >= 500:
            DisplayQueueManager.close_connection("tester_C")
            DisplayQueueManager.update_data("tester_A", {"TextBox": ["Goodbye", "For", "Now"]})
        time.sleep(0.01)
        # print(running)
    return


def wait_for_exit():
    input("Display Exit Started")
    CurrentDisplayState.change_state(False)
    return


def show_display():  # thread
    running = True
    loop_count = 0
    while running:
        if CurrentDisplayState.get_state():
            try:
                loop_count = ui_manager.main(DisplayQueueManager, loop_count)
            except KeyboardInterrupt:
                logging.exception("A display error has occurred, the display has been closed to prevent program exit.")
                time.sleep(0.1)
                print("Catch ID: 00")
                return
            if loop_count == "DisplayError":
                logging.exception("A display error has occurred, the display has been closed to prevent program exit.")
                time.sleep(0.1)
                print("Catch ID: 01")
                return
        else:
            logging.exception("A display error has occurred, the display has been closed to prevent program exit.")
            time.sleep(0.1)
            print("Catch ID: 02")
            return
        # print(loop_count)


def exit_protocol():
    print("Closing")
    ui_manager.close_display()
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
