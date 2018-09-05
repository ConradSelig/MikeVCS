from DatabaseManager import db_manager

import gender_guesser.detector as gender

from random import randint
import os


def get_header(name):

    # list of cases where I know that the database does not match
    special_cases = [["Laine", "male"]]

    gd = gender.Detector()

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
