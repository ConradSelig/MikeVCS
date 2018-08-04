import imaplib
import email
import time


'''
    Function Writer: Conrad Selig
    Date: 07/08/2018
    Parameters: None
    Inputs: None
    Returns: List of un-read emails
'''
def get_email_stack():

    #insansiating the list that will store the un-read emails
    received = []

    #loops until broken
    while True:
        #appending the next email using the _get_email_stack() function
        received.append(_get_next_email())
        #check if the last email == None or 1 (indicating end of unread emails
        if received[-1] is None or received[-1] == 1:
            #delete that last element
            del received[-1]
            #return the list of emails
            return received


'''
    Function Writer: Conrad Selig
    Date: 07/08/2018
    Parameters: None
    Inputs: Google Calendar API (using imaplib)
    Returns: Most recent un-read email
'''
def _get_next_email():

    received = []  # addr, name, subject, body

    # try surrounds until end of function, this is just a safety precaution to make sure
    # connections to servers to do cause errors when user stops program in the middle of
    # a retrieval operation.
    try:
        # loop will attempt to connect to host once every 10 seconds for 5 minutes or until it connects.
        for i in range(30):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                break
            except Exception:
                time.sleep(10)
                print("ERR (1)", end=" ")
                continue
        #if it can't connect, return nothing (no new messages)
        else:
            return 1

        # loop will attempt to connect to host once every 10 seconds for 5 minutes or until it connects.
        for i in range(30):
            try:
                mail.login("mike.adam.simon@gmail.com", "8R.wreyK_+t?AL9z")
                break
            except Exception:
                time.sleep(10)
                print("ERR (2)", end=" ")
                continue
        #if it can't connect, return nothing (no new messages)
        else:
            return 1

        #getting emails from mailbox, try except for server errors. If error, try again every 10 seconds for 5 minutes
        for i in range(30):
            try:
                mail.list()
                mail.select("inbox")
                break
            except Exception:
                time.sleep(10)
                print("ERR (3)", end=" ")
                continue
        #if it can't connect, return nothing (no new messages)
        else:
            return 1

        # accounting for server errors, check every 10 seconds for 5 minutes
        for i in range(30):
            try:
                #retrive all unseen messages
                result, data = mail.uid('search', None, "UNSEEN")  # search and return uids
                break
            except Exception:
                time.sleep(10)
                print("ERR (4)", end=" ")
                continue
        #if it can't connect, return nothing (no new messages)
        else:
            return 1

        # due to uid search, if no new emails found, will return empty byte array
        if data != [b'']:

            # get email ID
            latest_email_uid = data[0].split()[-1]

            # RFC822 is code for mail body
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')

            raw_email = data[0][1]

            # turns raw_email into a usable data type
            email_message = email.message_from_bytes(raw_email)

            #todo: add message attachment saving

            #build received array, this will later turn into reply_data
            received.append(email.utils.parseaddr(email_message["From"])[1])
            received.append(email.utils.parseaddr(email_message["From"])[0].split(" "))
            received.append(str(email.header.decode_header(email_message['Subject'])[0])[2:-8])

            # this is for after attachment is pulled off, also a redundant check is present just in case
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    # skip any text/plain (txt) attachments
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        received.append(part.get_payload(decode=True))  # decode
                        break
            # not multipart - i.e. plain text, no attachments, keeping fingers crossed
            else:
                received.append(email_message.get_payload(decode=True))

            return received

        else:
            return None

    #this is so that a nasty stack trace does not pop up if this function is cut shorts by program end
    except KeyboardInterrupt:
        print("Keyboard Interrupt, program ending")
        exit()