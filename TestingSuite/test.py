from UI import ui_manager as ui
import datetime


def test_display():

    ui.DisplayQueueManager.request_connection(["Main"], {"color": ui.YELLOW, "title": "Display Test",
                                                         "TextBox": ["Line A", "Line B", "Line C", "Lifespan = 3"],
                                                         "lifespan": 3})

    return 0
