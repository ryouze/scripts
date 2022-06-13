"""translate between english and polish (1)"""
import logging

# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def lstr(lang_db, name="", category="", language="en", return_available_categories=False, filename="./input/lang_db.json"):
    """
    Get localized string in either English or Polish.
    If 'return_available_categories' is True then all internal strings are returned as categorized dictionary.
    Return None if failed.
    """
    logging.debug(f"requested: {name=}, {category=}, {language=}, {return_available_categories=}")
    # if asked to return all available strings as a categorized dictionary, return early
    if return_available_categories is True:
        r = {"column": list(lang_db["english_columns"].keys()),
             "answer": list(lang_db["english_answers"].keys())}
        return r
    # otherwise, translate
    # return english string from category:
    if language == "en":
        # column
        if category == "column":
            return lang_db["english_columns"].get(name, None)
        # answer
        else:
            return lang_db["english_answers"].get(name, None)
    # return polish string from category:
    elif language == "pl":
        # column
        if category == "column":
            return lang_db["polish_columns"].get(name, None)
        # answer
        else:
            return lang_db["polish_answers"].get(name, None)
    else:
        logging.error(f"unknown language that is not 'en' or 'pl': {language}")
    return None


def translate_pl_to_en(obj, lang_db):
    """
    Return Polish dataframe where all columns and answers are translated to English.
    """
    # get all avilable categories and internal string names (e.g., {'column': ['rate_competence', 'is_l1]})
    internal_categories_db = lstr(lang_db, return_available_categories=True)
    # create dictionary: polish column name : english column name
    column_map = dict()
    for name in internal_categories_db["column"]:
        column_pl = lstr(lang_db, name, category="column", language="pl")
        column_en = lstr(lang_db, name, category="column", language="en")
        # if at rating, replace individual columns that contain numbers at the end
        # because normally, only the EXACT match will be replaced and not the rest
        if name == "rate_competence":
            obj.columns = [col.replace(column_pl, column_en) for col in obj.columns]
            continue
        column_map.update({column_pl:column_en})
        continue
    # rename polish to english columns
    obj.rename(columns=column_map, inplace=True)
    # create dictionary: polish answer name : english answer name
    answer_map = dict()
    for name in internal_categories_db["answer"]:
        answer_pl = lstr(lang_db, name, category="answer", language="pl")
        answer_en = lstr(lang_db, name, category="answer", language="en")
        answer_map.update({answer_pl:answer_en})
        continue
    # rename polish answers to english answers
    obj = obj.replace(answer_map)
    logging.info(f"ok: translated polish survey to english (rows={obj.shape[0]}, columns={obj.shape[1]})")
    return obj
