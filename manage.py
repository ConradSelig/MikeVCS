from UI import ui_manager

import logging


class DisplayState:

    state = type(bool)

    def __init__(self):
        self.state = True

    def get_state(self):
        return self.state

    def change_state(self, new_state):
        logging.exception("A display error has occurred, the display has been closed to prevent program exit.")
        self.state = new_state


def main():
    DisplayQueueManager = ui_manager.QueueHandler()

    DisplayQueueManager.request_connection(["Main"], {"color": ui_manager.GREEN, "title": "tester_A"})
    DisplayQueueManager.request_connection(["AI"], {"color": ui_manager.GREEN, "title": "tester_B"})
    DisplayQueueManager.request_connection(["Database"], {"color": ui_manager.GREEN, "title": "tester_C"})
    DisplayQueueManager.request_connection(["Display"], {"color": ui_manager.RED, "title": "tester_D"})
    DisplayQueueManager.request_connection(["Habit"], {"color": ui_manager.RED, "title": "tester_E"})
    DisplayQueueManager.request_connection(["Email"], {"color": ui_manager.RED, "title": "tester_F"})

    running = True
    show_display = DisplayState()
    loop_count = 0
    tick_count = 0
    while running:
        tick_count += 1
        if show_display.get_state():
            loop_count = ui_manager.main(DisplayQueueManager, loop_count)
            if loop_count == "DisplayError":
                show_display.change_state(False)
        else:
            ui_manager.close_display()
        if tick_count >= 1000:
            DisplayQueueManager.close_connection("tester_C")
    return


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
