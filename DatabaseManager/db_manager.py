from UI import ui_manager as ui

from math import floor, log10
from datetime import datetime
import time
import ast
import os
import re

from Robinhood import Robinhood

DATABASE_PATH = re.search("(.*)\\\\.*", os.path.realpath(__file__)).group(1) + "\\Database\\"


def build_portfolio_report():
    """
    Build a report of my stock portfolio, runs once a day at the end of market hours
    :return: None
    """

    # id for the display
    this_id = str(datetime.now())
    # update the display
    ui.DisplayQueueManager.request_connection(["Main", "Database"], {"title": "Stock Portfolio",
                                                                     "color": ui.YELLOW,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Building end of day report..."]})

    # get the file data for the minute reports
    portfolio_data = get_file_data("non_static\\stock_portfolio.txt")
    # initialize the list that will eventually be joined into the report
    report_data = []
    # for each line in the data
    for index, line in enumerate(portfolio_data):
        # build it into a processable list
        portfolio_data[index] = portfolio_data[index].split("; ")
        portfolio_data[index][1] = float(portfolio_data[index][1].replace("\n", ""))
    # calculate the net change over the day
    days_change = round(portfolio_data[-1][1] - portfolio_data[0][1], 4)
    # calculate the percentage of that change
    days_percent_change = days_change / portfolio_data[0][1]

    current_date = str(datetime.now().date()).split("-")

    # though next 12 lines, build the basic report values
    report_data.append("Portfolio Report for: " + current_date[1] + "/" + current_date[2] + "/" + current_date[0])
    report_data.append("Current Value: " + format(portfolio_data[-1][1], ".4f"))
    if days_change == 0:
        report_data.append("Portfolio's value did not change for the day")
    elif days_change > 0:
        report_data.append("Value Gained over day: $" + format(days_change, ".4f"))
        report_data.append("Percent Increased over day: " +
                           str(round(days_percent_change, -int(floor(log10(abs(days_percent_change)))))) + "%")
    else:
        report_data.append("Value Lost over day: $" + format(days_change, ".4f"))
        report_data.append("Percent Decreased over day: " +
                           str(round(days_percent_change, -int(floor(log10(abs(days_percent_change)))))) + "%")

    # login to robinhood
    robin_trader = Robinhood()
    try:
        robin_trader.login("ConradSelig", open(DATABASE_PATH + "static\\pass.txt", "r").read())
    except (Exception, BaseException):
        # update the display
        ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                               "color": ui.RED,
                                                               "TextBox": ["Building end of day report...",
                                                                           "   CONNECTION FAILED"]})
        return

    # collect the stocks owned from robinhood
    dsecowned = robin_trader.securities_owned()["results"]
    report_data.append("\nStocks Owned: ")
    # for each stock owned
    for position in dsecowned:
        # write the metadata for that report
        id = position['instrument'].split('/')[4]
        if float(position['quantity']) > 0:
            report_data.append("   Stock Name: " + robin_trader.instrument(id)['name'])
            report_data.append("   Stock Symbol: " + robin_trader.instrument(id)['symbol'])
            num_owned = position['quantity']
            report_data.append("      Number Owned: " + num_owned)
            value_per = robin_trader.bid_price(robin_trader.instrument(id)['symbol'])[0][0]
            report_data.append("      Value per Stock: " + format(float(value_per), ".4f"))
            report_data.append("      Portfolio Value: " + format((float(num_owned) * float(value_per)), ".4f"))

    # wait for the display to catch up
    time.sleep(1)
    # update the display
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database..."]})

    # write the report to the database
    write_file_data("non_static\\portfolio_report.txt", "\n".join(report_data))

    # wait for the display to catch up
    time.sleep(1)
    # update the display
    ui.DisplayQueueManager.update_data("Stock Portfolio", {"unique_id": this_id,
                                                           "color": ui.GREEN,
                                                           "TextBox": ["Building end of day report...",
                                                                       "   Built.",
                                                                       "Writing to Database...",
                                                                       "   Written."],
                                                           "lifespan": 3})

    return


def update_stock_portfolio_record():
    """
    Collects the current portfolio value and writes it to the database
    :return: None
    """
    # open the known reports file and read the data. Reading the data for the display
    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "r")
    excising_data = file.readlines()
    file.close()

    # id for the display
    this_id = str(datetime.now())
    # update the display
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Portfolio Record",
                                                             "color": ui.YELLOW,
                                                             "unique_id": this_id,
                                                             "TextBox": ["Number of old records:",
                                                                         "   " + str(len(excising_data)),
                                                                         "",
                                                                         "Adding new record..."]})

    # login to robinhood
    robin_trader = Robinhood()
    try:
        robin_trader.login("ConradSelig", open(DATABASE_PATH + "static\\pass.txt", "r").read())
    except (Exception, BaseException):
        # update the display
        ui.DisplayQueueManager.update_data("Updating Portfolio Record", {"color": ui.RED,
                                                                         "unique_id": this_id,
                                                                         "TextBox": ["Number of old records:",
                                                                                     "   " + str(len(excising_data)),
                                                                                     "",
                                                                                     "Adding new record...",
                                                                                     "   LOGIN FAILED"],
                                                                         "lifespan": 5})
        return

    profile_data = robin_trader.portfolios()

    # open the database file and write the new record
    file = open(DATABASE_PATH + "non_static\\stock_portfolio.txt", "a")
    file.write(str(datetime.now()) + "; " + profile_data["equity"] + "\n")
    file.close()

    # update the display
    ui.DisplayQueueManager.update_data("Updating Portfolio Record", {"color": ui.GREEN,
                                                                     "unique_id": this_id,
                                                                     "TextBox": ["Number of old records:",
                                                                                 "   " + str(len(excising_data)),
                                                                                 "",
                                                                                 "Adding new record...",
                                                                                 "   Done"],
                                                                     "lifespan": 3})

    return


def store_calendar_events(new_events):
    """
    Take in the new events and write the events to the database
    :param new_events: string of calendar events
    :return: None
    """
    # update the display
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Updating Calendar",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Opening the database..."]})

    # wait for the display to catch up
    time.sleep(1)
    # update the display
    ui.DisplayQueueManager.update_data("Updating Calendar", {"TextBox": ["Opening the database...",
                                                                         "   Complete",
                                                                         "Adding new Events..."]})
    # open the file for writing
    file = open(DATABASE_PATH + "non_static\\calendar_events.txt", "w")

    # count for the new events
    added_events = 0
    # for each new event
    for event in new_events:
        # if that event is not a known event
        try:
            # write the event to the file
            file.write(str(event) + "\n")
        except MemoryError:
            ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.RED,
                                                                     "TextBox": ["Opening the database...",
                                                                                 "   Complete",
                                                                                 "Adding new Events...",
                                                                                 "   FAILED (MemoryError)"],
                                                                     "lifespan": 15})
            return
        added_events += 1

    # close the file
    file.close()

    # wait for the display to catch up
    time.sleep(1)
    # update the display
    ui.DisplayQueueManager.update_data("Updating Calendar", {"color": ui.GREEN,
                                                             "TextBox": ["Opening the database...",
                                                                         "   Complete",
                                                                         "Adding new Events...",
                                                                         "   Events Added "
                                                                         "(" + str(added_events) + ")"],
                                                             "lifespan": 3})

    return


def parse_calendar_event(event):
    """
    Takes in an event string read from google API or database, parses into usable list
    :param event: string event
    :return: list event
    """
    # parse the data out of the string
    date_re = re.search("^\[\['(..)', '(..)', '(....)']", event)
    # build the data ordered for the datetime library
    date = [date_re.group(1), date_re.group(2), date_re.group(3)]
    # parse the event times and name from the string
    time_name_re = re.search(".{24}(..:..)', '(..:..)', '(.*)']$", event)
    # build into list including the date list
    event = [date, time_name_re.group(1), time_name_re.group(2), time_name_re.group(3)]
    # return the parsed event.
    return event


def get_file_data(file_name, read_lines=True):
    """
    Instead of having each module read from the database, the modules will go through this function in the db_manager
    to get data from the database.
    :param file_name: Does not include the DATABASE_PATH, id "non_static\\calendar_events.txt"
    :param read_lines: optional modifier, specifies the read mode of the function
    :return: File data as a string or a list
    """

    # parse the file_name with the DATABASE_PATH
    file_name = DATABASE_PATH + file_name
    # open the file
    file = open(file_name, "r")

    # if the file is being read as a list
    if read_lines:
        # read with readlines
        data = file.readlines()
    # else being read as a string
    else:
        # read as a single string
        data = file.read()
    # close the file
    file.close()
    # return the file data.
    return data


def write_file_data(file_name, data, append=False):
    """
    Instead of having each module write to the database, the modules will go through this function in the db_manager
    to add data to the database.
    :param file_name: Does not include the DATABASE_PATH, id "non_static\\calendar_events.txt"
    :param data: The data being writen, does not have to be string type.
    :param append: optional modifier, changes what mode the file is opened in.
    :return: None
    """

    # parse the file name to include the database path
    file_name = DATABASE_PATH + file_name
    # open the file with the type specified by append
    file = open(file_name, "a" if append else "w")
    # write the data casted as a string
    file.write(str(data))
    # close the file
    file.close()

    return


def check_database():
    """
    Function to make sure all needed files in the database, this is to help prevent errors later on.
    """

    # update the display
    ui.DisplayQueueManager.request_connection(["Database"], {"title": "Database Check",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Looking for errors..."]})

    # get a list of all contact and user data files
    metadata_files = os.listdir(DATABASE_PATH + "contact_metadata\\")
    user_files = os.listdir(DATABASE_PATH + "user_data\\")

    # wait for the display to catch up
    time.sleep(1)

    # update the display
    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users."],
                                                          "color": ui.YELLOW if len(metadata_files) == len(user_files)
                                                          else ui.RED})

    # wait for the display to catch up
    time.sleep(0.5)

    # if the file counts do not match
    if len(metadata_files) != len(user_files):

        # update the display
        ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                          "   " + str(
                                                                              len(metadata_files)) + " metadata.",
                                                                          "   " + str(len(user_files)) + " users.",
                                                                          "Repairing..."]})

        # if there are more user files than contact files
        if len(metadata_files) < len(user_files):
            # for each user file
            for user_file in user_files:
                # if that user file is not a contact file
                if user_file not in metadata_files:
                    # create that contact folder and its required metadata.txt
                    os.mkdir(DATABASE_PATH + "contact_metadata\\" + user_file)
                    open(DATABASE_PATH + "contact_metadata\\" + user_file + "\\metadata.txt", "w").close()

        # if there are more contact files than user files
        elif len(user_files) < len(metadata_files):
            # for each contact file
            for metadata_file in metadata_files:
                # if that contact file is not a user file
                if metadata_file not in user_files:
                    # create the user folder and its required files
                    os.mkdir(DATABASE_PATH + "user_data\\" + metadata_file)
                    open(DATABASE_PATH + "user_data\\" + metadata_file + "\\habits.txt", "w").close()
                    open(DATABASE_PATH + "user_data\\" + metadata_file + "\\metadata.txt", "w").close()

    # update the file lists
    metadata_files = os.listdir(DATABASE_PATH + "contact_metadata\\")
    user_files = os.listdir(DATABASE_PATH + "user_data\\")

    # finish waiting for the display to catch up
    time.sleep(0.5)

    # update the display
    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files..."],
                                                          "color": ui.YELLOW if len(metadata_files) == len(user_files)
                                                          else ui.RED})

    # counts the number of errors required
    file_errors = 0

    # for each file in each of the user folders. Try to open it, check for a valid read, and close it.
    # If no valid read, create the file.
    for user_file in user_files:
        try:
            open(DATABASE_PATH + "user_data\\" + user_file + "\\habits.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\habits.txt", "w").close()
        try:
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "w").close()

    # for each file in each of the contact folders. Try to open it, check for a valid read, and close it.
    # If no valid read, create the file.
    for metadata_file in metadata_files:
        try:
            open(DATABASE_PATH + "contact_metadata\\" + metadata_file + "\\metadata.txt", "r").close()
        except FileNotFoundError:
            file_errors += 1
            open(DATABASE_PATH + "user_data\\" + user_file + "\\metadata.txt", "w").close()

    # wait for the display to catch up
    time.sleep(1)

    # update the display
    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files...",
                                                                      "   Complete",
                                                                      "   (" + str(file_errors) + " repairs made)"],
                                                          "color": ui.YELLOW})

    # wait for the display to catch up
    time.sleep(1)

    # update the display
    ui.DisplayQueueManager.update_data("Database Check", {"TextBox": ["Looking for errors...",
                                                                      "   " + str(len(metadata_files)) + " metadata.",
                                                                      "   " + str(len(user_files)) + " users.",
                                                                      "Checking for missing files...",
                                                                      "   Complete",
                                                                      "   (" + str(file_errors) + " repairs made)",
                                                                      "",
                                                                      "Check complete!"],
                                                          "color": ui.GREEN,
                                                          "lifespan": 3})


def get_contact_metadata(contact_name, tag="") -> object:
    """
    :param contact_name: ["first_name", "last_name"]. Used to find the contact folder
    :param tag: optional. Used to pull a dictionary tag from the metadata file. If not provided the entire dictionary
                is returned.
    :return: -1 if no tag or file found. metadata dict[key] if key provided. metadata dict if no key provided.
    """
    # for each folder in the contact_metadata Database folder
    for folder in os.listdir(DATABASE_PATH + "contact_metadata\\"):
        # if the folder name matches the given name
        if folder == contact_name[0].title() + "-" + contact_name[1].title():

            # open the file, read the data as a single string
            file = open(DATABASE_PATH + "contact_metadata\\" + folder + "\\metadata.txt", "r")
            data = file.read()
            file.close()

            # turn the data into an actual dictionary type.
            try:
                data = ast.literal_eval(data)
            except SyntaxError:
                return -1

            # if a tag is provided
            if tag != "":

                # try catches cases where the tag does not exist
                try:
                    # return the metadata tag
                    return data[tag]
                except KeyError:
                    # key not found, return -1
                    return -1
            # no key provided, return entire dict
            return data
    # contact_metadata folder not found, return -1
    return -1
