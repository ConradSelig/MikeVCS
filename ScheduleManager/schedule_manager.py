#!/usr/bin/env python

from __future__ import print_function

from datetime import datetime
import os

import httplib2
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

from UI import ui_manager as ui

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def build_events():
    """
    Collect events from the Google Calendar API and parse them into a usable form.
    :return: Calendar Events (list)
    """

    # update the display
    ui.DisplayQueueManager.request_connection(["Schedule"], {"title": "Building Calendar",
                                                             "color": ui.YELLOW,
                                                             "TextBox": ["Getting Credentials"]})

    # get the api credentials
    credentials = _get_credentials()
    # update the display
    ui.DisplayQueueManager.update_data("Building Calendar", {"TextBox": ["Getting Credentials",
                                                                         "   Collected"]})
    # create a connection to the api
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # get the curent time
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # designate how the request should be make
    events_result = service.events().list(
        calendarId='primary', timeMin=now, singleEvents=True,
        orderBy='startTime').execute()
    # actually collect the events
    events = events_result.get('items', [])

    all_events = []

    if not events:
        print('No upcoming events found.')

    # for every collected event
    for event in events:
        try:
            # if event was collected correctly
            if event is not None:
                # collect the parts of the event
                date = event['start'].get('dateTime')[0:10]
                start = event['start'].get('dateTime')[11:16]
                end = event['end'].get('dateTime')[11:16]
                location = event['location']
                # parse into string
                all_events.append(str(date) + "&&" +
                                  str(start) + "&&" +
                                  str(end) + "&&" +
                                  str(event['summary']) + "&&" +
                                  location + "\n")
        # if an error occurred due to google calendar syntax
        except (Exception, BaseException):
            continue

    # for every collected event
    for i in range(len(all_events)):
        # parse into list
        all_events[i] = all_events[i].split("&&")
        all_events[i][-1] = all_events[i][-1].rstrip()
        all_events[i][0] = all_events[i][0].split("-")

        # rearrange the date
        all_events[i][0][0], all_events[i][0][1], all_events[i][0][2] = \
            all_events[i][0][1], all_events[i][0][2], all_events[i][0][0]

    # update the display
    ui.DisplayQueueManager.update_data("Building Calendar", {"color": ui.GREEN,
                                                             "lifespan": 3,
                                                             "TextBox": ["Getting Credentials",
                                                                         "   Collected",
                                                                         "Events Built",
                                                                         "   (" + str(len(all_events)) + " events)"]})

    return all_events


def _get_credentials():
    """
    Gets valid user credentials from storage.
       If nothing has been stored, or if the stored credentials are invalid,
       the OAuth2 flow is completed to obtain the new credentials.
    :return: Credentials, the obtained credential.
    """
    # used to locate files
    home_dir = os.path.expanduser('~')
    # locate the credentials file
    credential_dir = os.path.join(home_dir, '.credentials')
    # if not found
    if not os.path.exists(credential_dir):
        # create it
        os.makedirs(credential_dir)
    # locate the actual collector
    credential_path = os.path.join(credential_dir,
                                   'calendar-python.json')

    # parse into object used by the API
    store = Storage(credential_path)
    credentials = store.get()
    # if the credentials are valid
    if not credentials or credentials.invalid:
        # collect the actual credentials
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # parse based on python version and store
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    # return the credentials for use
    return credentials
