from UI import ui_manager as ui

import datetime
import time


def test_display():

    ui.DisplayQueueManager.request_connection(["Main"], {"color": ui.YELLOW, "title": "Initializing Display"})
    time.sleep(1)
    ui.DisplayQueueManager.update_data("Initializing Display", {"TextBox": ["Display Objects Built"]})
    time.sleep(1)
    ui.DisplayQueueManager.update_data("Initializing Display", {"color": ui.GREEN,
                                                                "TextBox": ["Display Object Built",
                                                                            ""
                                                                            "Initialization Complete"],
                                                                "lifespan": 2})

    return 0
