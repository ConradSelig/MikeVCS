from DatabaseManager import db_manager

import gender_guesser.detector as gender

from random import randint

import os
import re

def get_header(name):
    """
    Builds a header for each email based off the gender of the person who sent the email
    :param name: list ["first name", "last name"]
    :return: string header
    """

    # building the gender detector object
    gd = gender.Detector()

    # getting the gender from the detector
    this_gender = gd.get_gender(name[0].title()).lower()

    # checking special cases
    special_case = db_manager.get_contact_metadata(name, "gender")
    if special_case != -1:
        this_gender = special_case

    # picking male or female, if a-gender name, use "first name last name"
    if "female" in this_gender:
        # half and half chance to in
        # include "dear"
        if randint(0, 1) == 0:
            return "Dear Ms. " + name[0].title() + ",\n\n"
        else:
            return "Ms. " + name[0].title() + ",\n\n"\

    elif "male" in this_gender:
        # half and half chance to include "dear"
        if randint(0, 1) == 0:
            return "Dear Mr. " + name[1].title() + ",\n\n"
        else:
            return "Mr. " + name[1].title() + ",\n\n"\

    else:

        # half and half chance to include "dear"
        if randint(0, 1) == 0:
            return "Dear " + name[0] + " " + name[1] + ",\n\n"
        else:
            return name[0] + " " + name[1] + ",\n\n"


def parse_message(text):

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    if isinstance(text, str):
        text = text.split("\n")

    for index, line in enumerate(text):
        if "database value" in line or "database file" in line:
            files = os.listdir(db_manager.DATABASE_PATH + "non_static")
            files += os.listdir(db_manager.DATABASE_PATH + "static")
            print("\t", files)

    return
