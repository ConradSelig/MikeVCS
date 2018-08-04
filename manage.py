from UI import ui_manager

import logging


def main():
    DisplayQueueManager = ui_manager.QueueHandler()

    DisplayQueueManager.request_connection(["Main"])
    DisplayQueueManager.request_connection(["AI"])
    DisplayQueueManager.request_connection(["Database"])
    DisplayQueueManager.request_connection(["Display"])
    DisplayQueueManager.request_connection(["Habit"])
    DisplayQueueManager.request_connection(["Email"])

    running, show_display = True, True
    loop_count = 0
    while running:
        if show_display:
            loop_count = ui_manager.main(DisplayQueueManager, loop_count)
    return


def exit_protocol():
    print("Closing")
    ui_manager.close_display()
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_protocol()
    except (BaseException, Exception):
        print("\n\n")
        logging.exception("A Fatal Error has Occured")
        print("\n\n")
        exit_protocol()
