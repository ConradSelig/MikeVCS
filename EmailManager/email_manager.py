from UI import ui_manager as ui

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import smtplib
import imaplib
import email
import time


def get_email_stack():
    """
    collect a list containing one instance for each unprocessed email.
    :return: list of dictionaries containing the unread emails, or None
    """
    print("Getting email stack")

    # instantiating the list that will store the un-read emails
    received = []

    # loops until broken
    while True:
        # appending the next email using the _get_email_stack() function
        received.append(_get_next_email())
        # check if the last email == None or 1 (indicating end of unread emails
        if received[-1] is None or received[-1] == 1:
            # delete that last element
            del received[-1]
            # return the list of emails
            return received


def _get_next_email():
    """
    Gets the next email from the inbox, private function - should only be used by get_email_stack()
    :return: a single email dictionary, None if no new emails, 1 if an error occurred.
    """
    received = {"addr": "", "name": "", "subject": "", "body": ""}  # address, name, subject, body

    # try surrounds until end of function, this is just a safety precaution to make sure
    # connections to servers to do cause errors when user stops program in the middle of
    # a retrieval operation.
    try:
        # loop will attempt to connect to host once every 10 seconds for 5 minutes or until it connects.
        for i in range(30):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                break
            except (BaseException, Exception):
                time.sleep(10)
                print("ERR (1)", end=" ")
                continue
        # if it can't connect, return nothing (no new messages)
        else:
            return 1

        # loop will attempt to connect to host once every 10 seconds for 5 minutes or until it connects.
        for i in range(30):
            try:
                mail.login("mike.adam.simon@gmail.com", "8R.wreyK_+t?AL9z")
                break
            except (BaseException, Exception):
                time.sleep(10)
                print("ERR (2)", end=" ")
                continue
        # if it can't connect, return nothing (no new messages)
        else:
            return 1

        # getting emails from mailbox, try except for server errors. If error, try again every 10 seconds for 5 minutes
        for i in range(30):
            try:
                mail.list()
                mail.select("inbox")
                break
            except (BaseException, Exception):
                time.sleep(10)
                print("ERR (3)", end=" ")
                continue
        # if it can't connect, return nothing (no new messages)
        else:
            return 1

        # accounting for server errors, check every 10 seconds for 5 minutes
        for i in range(30):
            try:
                # retrieve all unseen messages
                result, data = mail.uid('search', None, "UNSEEN")  # search and return uids
                break
            except (BaseException, Exception):
                time.sleep(10)
                print("ERR (4)", end=" ")
                continue
        # if it can't connect, return nothing (no new messages)
        else:
            return 1

        # due to uid search, if no new emails found, will return empty byte array
        if data != [b'']:

            print("Adding Incoming Email Event")
            this_id = str(datetime.now())
            ui.DisplayQueueManager.request_connection(["Email"], {"title": "Incoming Email",
                                                                  "color": ui.YELLOW,
                                                                  "TextBox": ["New Email Detected.",
                                                                              "Parsing Message..."],
                                                                  "unique_id": this_id})

            # get email ID
            latest_email_uid = data[0].split()[-1]

            # RFC822 is code for mail body
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')

            raw_email = data[0][1]

            # turns raw_email into a usable data type
            email_message = email.message_from_bytes(raw_email)

            # todo: add message attachment saving

            # build received array, this will later turn into reply_data
            received["addr"] = (email.utils.parseaddr(email_message["From"])[1])
            received["name"] = (email.utils.parseaddr(email_message["From"])[0].split(" "))
            received["subject"] = (str(email.header.decode_header(email_message['Subject'])[0])[2:-8])

            # this is for after attachment is pulled off, also a redundant check is present just in case
            # Currently not supporting attachments.
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    # skip any text/plain (txt) attachments
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        received["body"] = part.get_payload(decode=True).decode("utf-8")  # decode
                        break

            time.sleep(2)

            ui.DisplayQueueManager.update_data("Incoming Email", {"color": ui.GREEN,
                                                                  "TextBox": ["New Email Detected.",
                                                                              "Parsing Message...",
                                                                              "",
                                                                              "Message Received From:",
                                                                              received["name"][0] + " " +
                                                                              received["name"][1],
                                                                              "",
                                                                              "Parsing Successful."],
                                                                  "lifespan": 3},
                                               unique_id=this_id)
            print("Message Data:", received)

            return received

        else:
            return None

    # this is so that a nasty stack trace does not pop up if this function is cut shorts by program end
    except KeyboardInterrupt:
        print("Keyboard Interrupt, program ending")
        exit()


def send_email(email_data, addr="", subject="", body=""):
    """
    Collect required data for sending an email, and send the message. Uses email_data if all keys present, else uses
    optional params
    :param email_data: dict, should contain the following fields as keys:
    :param addr: the address the email should be sent to
    :param subject: the subject of the email
    :param body: all of the text the email should contain
    """

    # custom ID for the UI.
    this_id = str(datetime.now())

    #update the display
    ui.DisplayQueueManager.request_connection(["Email"], {"title": "Sending Email",
                                                          "unique_id": this_id,
                                                          "color": ui.YELLOW,
                                                          "TextBox": ["Preparing message..."]})

    # fromaddr constant, every message is from Mike!
    fromaddr = "mike.adam.simon@gmail.com"

    # try to set the variables from the email_data dictionary. If any key not present use optional params.
    try:
        addr = email_data["addr"]
        subject = email_data["subject"]
        body = email_data["body"]
    except KeyError:
        # a single missing key indicates that email_data is not being used.
        # reset all variables to hand input.
        addr = addr
        subject = subject
        body = body

    # MIMEMultipart() object takes in easy input and builds a email friendly variable for sending
    msg = MIMEMultipart()

    # imputing data into msg
    msg["From"] = fromaddr
    msg["To"] = addr
    msg["Subject"] = subject

    # attach the body of the message as a MIMEText object for formatting reasons.
    msg.attach(MIMEText(body, "plain"))

    # update the display
    ui.DisplayQueueManager.update_data("Sending Email", {"unique_id": this_id,
                                                         "TextBox": ["Preparing message...",
                                                                     "   Built.",
                                                                     "",
                                                                     "Sending Message..."]})

    # block to login to email service, if network error occurs and cannot login, wait one second and try again.
    # Makes attempts for one minute.
    for i in range(60):
        try:
            # logging in, stops loop if successful
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "8R.wreyK_+t?AL9z")
            # adding email data (recall that msg is a MIME var)
            text = msg.as_string()

            # send it!
            server.sendmail(fromaddr, addr, text)

            # similar to .close() for a file, but signals to email server that all actions are complete
            server.quit()
            break

        # did any error occur
        except (Exception, BaseException):
            # update the display
            ui.DisplayQueueManager.update_data("Sending Email", {"unique_id": this_id,
                                                                 "color": ui.RED,
                                                                 "TextBox": ["Preparing message...",
                                                                             "   Built.",
                                                                             "",
                                                                             "Sending Message...",
                                                                             "   Connection Failure!",
                                                                             "Retrying..."]
                                                                 })
            # wait for the display to catch up
            time.sleep(1)

            # go back to start of loop, attempt to send the message again
            continue

    # update the display now that the message is sent
    ui.DisplayQueueManager.update_data("Sending Email", {"unique_id": this_id,
                                                         "color": ui.GREEN,
                                                         "TextBox": ["Preparing message...",
                                                                     "   Built.",
                                                                     "",
                                                                     "Sending Message...",
                                                                     "   Sent"],
                                                         "lifespan": 3})
