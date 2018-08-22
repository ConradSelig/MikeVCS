from UI import ui_manager as ui
import datetime


def test_display():

    ui.DisplayQueueManager.request_connection(["Main"], {"color": ui.YELLOW, "title": "Display Test",
                                                         "TextBox": ["Line A", "Line B", "Line C", "Lifespan = 3"],
                                                         "lifespan": 3})

    ui.DisplayQueueManager.request_connection(["Main"], {"color": ui.YELLOW, "title": "Display Test 2",
                                                         "TextBox": ["Line A", "Line B", "Line C", "Lifespan = 5"],
                                                         "lifespan": 5})

    return 0
