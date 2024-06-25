import json


def grab(fl):
    """
    Grabs the data that is in the folders
    :param fl: str full path to file
    :return:
    """
    with open(fl, "r") as f:
        r = json.load(f)

    return r

