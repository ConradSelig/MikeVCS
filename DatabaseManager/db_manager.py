from UI import ui_manager as ui

import time
import os
import re


def store_calendar_events(new_events):
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Adding Calendar Events",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Reading in known events..."]})
    events_file_path = re.search("(.*)\\\\.*", os.path.realpath(__file__)).group(1) + \
                       "\Database\\non_static\\calendar_events.txt"
    existing_events = get_file_data(events_file_path)
    time.sleep(1)
    ui.DisplayQueueManager.update_data("Adding Calendar Events", {"TextBox": ["Reading in known events...",
                                                                              "Compiled "
                                                                              "(" + str(len(existing_events)) + ")",
                                                                              "Adding new Events"]})
    file = open(events_file_path, "w")

    for index in range(len(existing_events)):
        existing_events[index] = existing_events[index].replace("\n", "")
        file.write(str(existing_events[index]))
    for event in new_events:
        if event not in existing_events:
            file.write(str(event) + "\n")
    file.close()
    time.sleep(1)

    ui.DisplayQueueManager.update_data("Adding Calendar Events", {"color": ui.GREEN,
                                                                  "TextBox": ["Reading in known events...",
                                                                              "   Compiled "
                                                                              "(" + str(len(existing_events)) + ")",
                                                                              "Adding new Events...",
                                                                              "   New Events Added"],
                                                                  "lifespan": 3})


def get_file_data(file_name, read_lines=True):
    file = open(file_name, "r")
    if read_lines:
        data = file.readlines()
    else:
        data = file.read()
    file.close()
    return data
