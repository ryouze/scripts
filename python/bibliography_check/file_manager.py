"""load txt file with bibliography"""
from os.path import exists
import logging

# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_file(location, encoding="utf-8"):
    """
    load txt file, return its content as list (each line = separate item)
    """
    if not exists(location):
        logging.error(f"input file doesn't exist, please create it: {location}")
        raise Exception
    # load txt file
    with open(location, "r", encoding=encoding) as f:
        f = f.readlines()
    # remove empty lines and trailing spaces
    f = [i.strip() for i in f if len(i) > 5 and i[0] != "#"]
    logging.info(f"ok: loaded a list of {len(f)} bibliographies from: {location}")
    return f
