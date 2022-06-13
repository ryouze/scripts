"""calculate means and other statistics (3)"""
from collections import Counter
import lang
import logging

# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def rename_columns(obj, list_columns, survey_lang):
    """
    return a pandas dataframe with columns renamed using list provided if their lengths match
    """
    # get column size for old vs. new
    old_size = obj.shape[1]
    new_size = len(list_columns)
    # if length of old columns is not the same as new columns, quit program
    if old_size != new_size:
        logging.error(f"custom column length '{new_size}' is not the same as the length of ratings columns '{old_size}' in the csv file ({survey_lang})")
        quit()
    # otherwise, rename columns
    obj.columns = list_columns
    logging.info(f"ok: renamed old columns to custom columns (survey: {survey_lang}): {obj.columns[:3]=}")
    return obj


def get_mean_per_language(obj, colname, colls_db, survey_lang, decimal_points=4):
    """
    return dataframe which contains mean per condition only
    """
    # (1) get dataframe containing ratings columns only
    obj = obj.filter(like=colname)
    # (2) rename dataframe to custom column names
    obj = rename_columns(obj, colls_db, survey_lang=survey_lang)
    # (3) group by identical category names
    obj = obj.groupby(level=0, axis=1)
    # (4) calculate means per condition
    obj = obj.mean().round(decimal_points)
    # obj_means[f"{survey_lang}_avg_mean"] = obj_means.mean(axis=1).round(decimal_points)
    # obj_means[f"{survey_lang}_stdev"] = obj_means.std(axis=1).round(decimal_points)
    # obj_means[f"{survey_lang}_min"] = obj.min(axis=1)
    # obj_means[f"{survey_lang}_max"] = obj.max(axis=1)
    logging.info(f"ok: calculated mean per condition ({survey_lang}): (columns: {obj.shape[1]}, rows: {obj.shape[0]})")
    return obj


def add_columns_to_means_df(obj_means, obj_original, colls_to_add, lang_db, survey_lang):
    """
    add specific columns from original dataframe (contains all columns) into dataframe (contains means columns only)
    """
    # (1) add language of survey at the beginning
    obj_means.insert(0, "Language", survey_lang)
    # (2) for each column provided (using internal naming system found in lang_db)
    for item in colls_to_add:
        english_column_name = lang.lstr(lang_db, item, category="column")
        # re-add it to obj_means as column
        obj_means[english_column_name] = obj_original[english_column_name]
        continue
    return obj_means


def get_means(obj, colls_db, lang_db, survey_lang):
    """
    return clean dataframe with means per condition and all columns, e.g., when were you born
    """
    # (1) get means only
    obj_means = get_mean_per_language(obj=obj,
                                      colname=lang.lstr(lang_db, "rate_competence", category="column"),
                                      colls_db=colls_db,
                                      survey_lang=survey_lang)
    # (2) add specific columns to english means (age, city size, gender, etc)
    colls_to_add = ["is_l1", "is_l2", "how_often", "age_begin_eng", "birth_year", "what_gender", "how_big_city", "which_uni_year"]
    obj_means_with_columns = add_columns_to_means_df(obj_means=obj_means,
                                                     obj_original=obj,
                                                     colls_to_add=colls_to_add,
                                                     lang_db=lang_db,
                                                     survey_lang=survey_lang)
    return obj_means_with_columns


def find_wrong_answers(obj, d_filter_conditions, survey_lang):
    """
    return list of rows that did not not match value (value) under columns (key)
    """
    # create list that will contain indexes (numbers) where wrong answers were found
    list_wrong_answers = list()
    # find rows under columns whose value doesn't match
    for colname, correct_answer in d_filter_conditions.items():
        # get dataframe containing only specific colname only
        c_obj = obj.filter(like=colname)
        logging.debug(f"checking column '{colname}' (survey: {survey_lang}) for answers that are not '{correct_answer}'")
        # find rows that do NOT match correct answer
        match = c_obj[c_obj[colname] != correct_answer]
        # convert dataframe to list
        match = match.index.tolist()
        if match:
            # if found wrong answers, append to list
            logging.warning(f"answer to '{colname}' (survey: {survey_lang}) is not '{correct_answer}' for following participants '{match}'")
            list_wrong_answers.extend(match)
        continue
    # turn repeating rows into single instances
    list_wrong_answers = list(set(list_wrong_answers))
    # calculate ratio of wrong answers
    ratio = round(((len(list_wrong_answers) / obj.shape[0]) * 100), 2)
    logging.info(f"ok: checked answers (survey: {survey_lang}) for '{list(d_filter_conditions.keys())}', result: {len(list_wrong_answers)} out of {obj.shape[0]} participants (ratio: {ratio}%)")
    return list_wrong_answers


def find_clickers(obj_means, obj_original, colname, max_clicker_ratio, survey_lang):
    """
    return list of rows where participant kept clicking the same answer
    if max_ratio is exceeded then row is marked as a clicker and removed
    """
    # create list that will contain indexes (numbers) where clickers were found
    list_clickers = list()
    # using old dataframe, get dataframe containing answers only
    obj = obj_original.filter(like=colname)
    # get total amount of answers, based on column length
    answers_amount = obj.shape[1]
    # for each row (participant)
    for index, row in obj.iterrows():
        # convert to list, get most occuring answer as tuple
        row = row.tolist()
        occurrence = Counter(row).most_common(1)[0]
        # calculate how often most occuring answer appears vs. total amount of answers
        ratio_percent = round(occurrence[1] / answers_amount * 100)
        # logging.info(f"row {index} (survey: {survey_lang}) has chosen the same answer '{occurrence[0]}' in {ratio_percent}% of answers ({answers_amount} answers vs. {occurrence[1]} occurences); {sorted(row)}; {min(row)=}; {max(row)=}")
        if ratio_percent > max_clicker_ratio:
            logging.warning(f"participant (survey: {survey_lang}): row '{index}' has same answer '{occurrence[0]}' in {ratio_percent}% of cases (cutoff: >{max_clicker_ratio}%)")
            list_clickers.append(index)
        continue
    # calculate ratio of clickers
    ratio = round(((len(list_clickers) / obj.shape[0]) * 100), 2)
    logging.info(f"ok: checked clickers (survey: {survey_lang}) at >{max_clicker_ratio}% cutoff, result: {len(list_clickers)} out of {obj.shape[0]} participants (ratio: {ratio}%)")
    return list_clickers


def drop_rows(obj, target_list, survey_lang):
    """
    drop rows from dataframe using list
    if list empty, nothing is dropped
    """
    # if not empty
    if target_list:
        r = obj.copy()
        # axis=0 - rows should be deleted; inplace=True - operation in the same dataframe
        r.drop(target_list, axis=0, inplace=True)
        # reset counting
        r.reset_index(drop=True, inplace=True)
        logging.info(f"ok: dropped {len(target_list)} rows: {obj.shape[0]} -> {r.shape[0]} (survey: {survey_lang})")
        return r
    logging.info(f"did not drop rows: {obj.shape[0]} (survey: {survey_lang})")
    return obj


def target_learn(obj, colname):
    """
    return a dictionary of the age at which the participants began to learn english (e.g., "7")
    """
    # get dataframe
    df_begin = obj.filter(like=colname)
    # get the single column that appears
    df_begin = df_begin[colname]
    # get rounded float
    mean_age = round(float(df_begin.mean()), 2)
    stdev = round(float(df_begin.std()), 2)
    min_age = round(float(df_begin.min()), 2)
    max_age = round(float(df_begin.max()), 2)
    # create dictionary that contains mean learn and standard deviation
    r = {
        "began learning english: mean age":mean_age,
        "began learning english: min age":min_age,
        "began learning english: max age":max_age,
        "began learning english: stdev":stdev
    }
    logging.info(f"calculated when began to learn english: {mean_age=}, {min_age=}, {max_age=}, {stdev=}")
    return r


def target_age(obj, colname, current_year=2022):
    """
    return a dictionary of the participants' ages (e.g., "22")
    """
    # get dataframe
    df_born = obj.filter(like=colname)
    # get the single column that appears
    df_born = df_born[colname]
    # get rounded float
    mean_birth = round(float(df_born.mean()), 2)
    stdev = round(float(df_born.std()), 2)
    min_birth = round(float(df_born.min()), 2)
    max_birth = round(float(df_born.max()), 2)
    # calculate age by substracting current year, e.g., 2022 - 1999
    mean_age = round((current_year - mean_birth), 2)
    min_age = round((current_year - max_birth), 2)
    max_age = round((current_year - min_birth), 2)
    # create dictionary that contains mean age and standard deviation
    r = {
        "age: mean age":mean_age,
        "age: min age":min_age,
        "age: max age":max_age,
        "age: stdev":stdev
    }
    logging.info(f"calculated age: {mean_age=}, {min_age=}, {max_age=}, {stdev=}")
    return r


def target_gender(obj, colname):
    """
    return a dictionary of participants' gender (e.g., "female")
    """
    # get dataframe
    df_gender = obj.filter(like=colname)
    # get the single column that appears
    df_gender = df_gender[colname]
    # get individual occurences
    gender_dataset = df_gender.value_counts(normalize=True)
    # convert to percentage with 1 decimal
    gender_dataset = gender_dataset.mul(100).round(1).astype(str) + '%'
    # convert to dictionary
    gender_dataset = gender_dataset.to_dict()
    logging.info(f"calculated gender: {gender_dataset=}")
    return gender_dataset


def target_city(obj, colname):
    """
    return a dictionary of participants' city size (e.g., "15,000 - 75,000 residents")
    """
    # get dataframe
    df_city = obj.filter(like=colname)
    # get the single column that appears
    df_city = df_city[colname]
    # get individual occurences
    city_dataset = df_city.value_counts(normalize=True)
    # convert to percentage with 1 decimal
    city_dataset = city_dataset.mul(100).round(1).astype(str) + '%'
    # convert to dictionary
    city_dataset = city_dataset.to_dict()
    logging.info(f"calculated city size: {city_dataset=}")
    return city_dataset


def target_uni(obj, colname):
    """
    return a dictionary of participants' current uni year
    """
    # get dataframe
    df_uni = obj.filter(like=colname)
    # get the single column that appears
    df_uni = df_uni[colname]
    # get individual occurences
    uni_dataset = df_uni.value_counts(normalize=True)
    # convert to percentage with 1 decimal
    uni_dataset = uni_dataset.mul(100).round(1).astype(str) + '%'
    # convert to dictionary
    uni_dataset = uni_dataset.to_dict()
    logging.info(f"calculated uni size: {uni_dataset=}")
    return uni_dataset


def rename_index_to_participant(obj, name="Participant"):
    """
    reset index, set it to start from 1, rename it to "Participant
    """
    # (1) reset index, set it to start from 1
    obj.reset_index(inplace=True, drop=True)
    obj.index += 1
    # (2) rename index to "Participant"
    obj.index.rename(name, inplace=True)
    return obj
