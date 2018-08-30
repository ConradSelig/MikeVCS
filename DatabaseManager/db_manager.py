from ScheduleManager import schedule_manager
from UI import ui_manager as ui

from datetime import datetime
import datetime as dt
import time
import os
import re

from Robinhood import Robinhood

LONG_UPDATE = datetime.now() - dt.timedelta(minutes=100)
REG_UPDATE = datetime.now() - dt.timedelta(minutes=100)
SHORT_UPDATE = datetime.now() - dt.timedelta(minutes=100)

DATABASE_PATH = re.search("(.*)\\\\.*", os.path.realpath(__file__)).group(1) + "\\Database\\"


def update_db():
    global LONG_UPDATE
    global REG_UPDATE
    global SHORT_UPDATE
    if datetime.now() > LONG_UPDATE + dt.timedelta(minutes=60):
        LONG_UPDATE = datetime.now()
    if datetime.now() > REG_UPDATE + dt.timedelta(minutes=15):
        REG_UPDATE = datetime.now()
        store_calendar_events(schedule_manager.build_events())
    if datetime.now() > SHORT_UPDATE + dt.timedelta(minutes=1):
        SHORT_UPDATE = datetime.now()
        update_stock_portfolio_record()


def update_stock_portfolio_record():

    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "r")
    excising_data = file.readlines()
    file.close()

    this_id = str(datetime.now())

    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Portfolio Record",
                                                             "color": ui.YELLOW,
                                                             "unique_id": this_id,
                                                             "TextBox": ["Number of old records:",
                                                                         "   " + str(len(excising_data)),
                                                                         "",
                                                                         "Adding new record..."]})

    robin_trader = Robinhood()
    robin_trader.login("ConradSelig", open(DATABASE_PATH + "static\\pass.txt", "r").read())
    profile_data = robin_trader.portfolios()

    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "a")
    file.write(str(datetime.now()) + "; " + profile_data["equity"] + "\n")
    file.close()

    ui.DisplayQueueManager.update_data("Updating Portfolio Record", {"color": ui.GREEN,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Number of old records:",
                                                                                 "   " + str(len(excising_data)),
                                                                                 "",
                                                                                 "Adding new record...",
                                                                                 "   Done"],
                                                                     "lifespan": 3})


def store_calendar_events(new_events):
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Calendar",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Reading in known events..."]})

    existing_events = get_file_data("non_static\\calendar_events.txt")
    time.sleep(1)
    ui.DisplayQueueManager.update_data("Updating Calendar", {"TextBox": ["Reading in known events...",
                                                                         "   Compiled "
                                                                         "(" + str(len(existing_events)) + ")",
                                                                         "Adding new Events..."]})
    file = open(DATABASE_PATH + "non_static\\calendar_events.txt", "w")

    for index, event in enumerate(existing_events):
        existing_events[index] = event.replace("\n", "")
        event = parse_calendar_event(event)
        datetime_string = event[0][0] + " " + event[0][1] + " " + event[0][2] + " " + event[1]
        datetime_event = datetime.strptime(datetime_string, "%m %d %Y %H:%M")
        if datetime_event > datetime.now():
            file.write(str(event))
    added_events = 0
    for event in new_events:
        if str(event) not in existing_events:
            file.write(str(event) + "\n")
            added_events += 1

    file.close()
    time.sleep(1)

    ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.GREEN,
                                                             "TextBox": ["Reading in known events...",
                                                                         "   Compiled "
                                                                         "(" + str(len(existing_events)) + ")",
                                                                         "Adding new Events...",
                                                                         "   New Events Added "
                                                                         "(" + str(added_events) + ")"],
                                                             "lifespan": 3})


def parse_calendar_event(event):
    date_re = re.search("^\[\['(..)', '(..)', '(....)']", event)
    date = [date_re.group(1), date_re.group(2), date_re.group(3)]
    time_name_re = re.search(".{24}(..:..)', '(..:..)', '(.*)']$", event)
    event = [date, time_name_re.group(1), time_name_re.group(2), time_name_re.group(3)]
    return event


def get_file_data(file_name, read_lines=True):
    file_name = DATABASE_PATH + file_name
    file = open(file_name, "r")
    if read_lines:
        data = file.readlines()
    else:
        data = file.read()
    file.close()
    return data


def write_file_data(file_name, data, append=False):
    file_name = DATABASE_PATH + file_name
    file = open(file_name, "a" if append else "w")
    file.write(data)
    file.close()
    return
