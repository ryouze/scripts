"""load and save files (2)"""
from json import load
from os import makedirs
from os.path import exists, split
import logging
import pandas as pd


# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_json(fn, encoding="utf-8"):
    """
    load json file, return its content as dictionary
    """
    try:
        with open(fn, "r", encoding=encoding) as f:
            # load to dictionary using json library
            r = load(f)
            logging.info(f"ok: loaded json from: {fn}")
    except Exception as e:
        # if failed, quit program
        logging.exception(f"failed to load json file; reason: {e}")
        quit()
    return r


def load_columns(fn, encoding="utf-8"):
    """
    load column names from text file and return its content as list
    """
    try:
        with open(fn, "r", encoding=encoding) as f:
            # read lines
            f = f.readlines()
        # drop items shorter than 4 characters or containing comment as the first character
        f = [i.strip() for i in f if len(i) > 3 and i[0] != "#"]
        # split at equal signs
        r = list()
        for item in f:
            s_item = item.split("=")
            # if got two items, get first item
            if len(s_item) == 2:
                s_item = s_item[0].strip()
            # if didn't get two items, use as-is
            else:
                s_item = item
                logging.warning(f"column name provided did not split at equal sign into two items: {s_item}; using '{item}' instead")
            r.append(s_item)
            # logging.debug(f"column name added: {s_item}")
            continue
        logging.info(f"ok: loaded '{len(r)}' column names to use as replacement (dropped: {len(f) - len(r)} lines)")
    except Exception as e:
        # if failed, quit program
        logging.exception(f"failed to load column file; reason: {e}")
        quit()
    return r


def load_csv(fn, survey_lang):
    """
    load csv and return its content as pandas dataframe
    """
    try:
        r = pd.read_csv(fn)
        logging.info(f"ok: loaded csv file ({survey_lang}): {fn} (columns: {r.shape[1]}, rows: {r.shape[0]})")
    except Exception as e:
        # if failed, quit program
        logging.exception(f"failed to load csv file ({survey_lang}); reason: {e}")
        quit()
    return r


def create_dir_if_doesnt_exist(fn):
    """
    checks if directory name containing file exists, creates if it doesn't
    e.g., "./output/stats.csv" will check for "./output" and create "./output" directory
    """
    # get directory name only
    dirname = split(fn)[0]
    # check if directory exists, create if doesn't
    if not exists(dirname):
        makedirs(dirname)
    return


def save_dataframe_as_csv(obj, fn, index=True):
    """
    save pandas dataframe as csv file
    if index is true then row numbers will be added on the left, as the first column
    """
    # check if directory exists, create if doesn't
    create_dir_if_doesnt_exist(fn)
    # save to csv
    obj.to_csv(fn, index=index)
    logging.info(f"ok: saved csv: {fn} (columns: {obj.shape[1]}, rows: {obj.shape[0]})")
    return


def save_dictionary_as_txt(obj, header, fn):
    """
    save dictionary as txt file, with each value preceded by a tab
    """
    # create long string
    to_save = f"{header}\n"
    for key, value in obj.items():
        to_save += f"\n[{key}]\n"
        for subkey, subvalue in value.items():
            to_save += f"\t{subkey} = {subvalue}\n"
            continue
        continue
    # check if directory exists, create if doesn't
    create_dir_if_doesnt_exist(fn=fn)
    # save to txt
    with open(fn, "w+") as file_write:
        file_write.write(to_save)
    logging.info(f"ok: saved txt: {fn}")
    return
