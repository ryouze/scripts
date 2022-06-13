"""compile results from other functions into single objects (4)"""
import fm
import lang
import logging
import pandas as pd
import target


# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_all(lang_db, colls_db, fn_survey_input_en, fn_survey_input_pl):
    """
    load custom columns (txt), 'survey_en' (dataframe), 'survey_pl' (dataframe)
    translate 'survey_pl' into english
    replace old columns with custom columns in 'survey_en' and 'survey_pl'
    group by conditions and calculate means of 'survey_en' and 'survey_pl'
    append old columns (e.g., when were you born?) to means of 'survey_en' and 'survey_pl'
    return: means of 'survey_en' and 'survey_pl' (+ their unprocessed variants)
    """
    # (1) load english csv file
    original_en = fm.load_csv(fn=fn_survey_input_en,
                              survey_lang="en")
    logging.info(f"english group is available ({original_en.shape[0]} participants)")
    # (2) get means for english group
    means_en = target.get_means(original_en,
                                colls_db=colls_db,
                                lang_db=lang_db,
                                survey_lang="en")
    # (3) load polish csv file, translate it to english
    original_pl = fm.load_csv(fn=fn_survey_input_pl,
                              survey_lang="pl")
    original_pl = lang.translate_pl_to_en(obj=original_pl,
                                          lang_db=lang_db)
    logging.info(f"polish group is available ({original_pl.shape[0]} participants)")
    # (4) get means for polish group
    means_pl = target.get_means(original_pl,
                                colls_db=colls_db,
                                lang_db=lang_db,
                                survey_lang="pl")
    return means_en, original_en, means_pl, original_pl


def remove_participants(lang_db, means_en, original_en, means_pl, original_pl, d_filter_conditions, max_clicker_ratio=80):
    """
    remove participants who did not answer with X to a question or kept clicking the same answer
    """
    # (1) set variables
    colname = lang.lstr(lang_db,"rate_competence", category="column")
    # (2) remove english participants who did not answer with X to a question
    list_wrong_en = target.find_wrong_answers(obj=means_en,
                                              d_filter_conditions=d_filter_conditions,
                                              survey_lang="en")
    means_en = target.drop_rows(obj=means_en,
                                target_list=list_wrong_en,
                                survey_lang="en")
    # (3) remove polish participants who did not answer with X to a question
    list_wrong_pl = target.find_wrong_answers(obj=means_pl,
                                              d_filter_conditions=d_filter_conditions,
                                              survey_lang="pl")
    means_pl = target.drop_rows(obj=means_pl,
                                target_list=list_wrong_pl,
                                survey_lang="pl")
    # (4) remove english participants who kept clicking the same answer
    list_clickers_en = target.find_clickers(obj_means=means_en,
                                            obj_original=original_en,
                                            colname=colname,
                                            max_clicker_ratio=max_clicker_ratio,
                                            survey_lang="en")
    means_en = target.drop_rows(obj=means_en,
                                target_list=list_clickers_en,
                                survey_lang="en")
    # (5) remove polish participants who kept clicking the same answer
    list_clickers_pl = target.find_clickers(obj_means=means_pl,
                                            obj_original=original_pl,
                                            colname=colname,
                                            max_clicker_ratio=max_clicker_ratio,
                                            survey_lang="pl")
    means_pl = target.drop_rows(obj=means_pl,
                                target_list=list_clickers_pl,
                                survey_lang="pl")
    return means_en, means_pl


def get_clean_dfs(lang_db, enabled, colls_db, fn_survey_input_en, fn_survey_input_pl, fn_survey_output_en, fn_survey_output_pl, max_clicker_ratio):
    """
    return processed english and polish survey with means and without clickers and participants who clicked the wrong answer
    """
    # (1) if asked to open survey and process csv from './input'
    if enabled["use_csv_from_input"] is True:
        logging.info("ok: loading raw csvs from input because 'use_csv_from_input' is True")
        # (I) load survey_en and survey_pl, get their means by condition; returns dictionary: means_en, original_en, means_pl, original_pl
        means_en, original_en, means_pl, original_pl = load_all(lang_db=lang_db,
                                                                colls_db=colls_db,
                                                                fn_survey_input_en=fn_survey_input_en,
                                                                fn_survey_input_pl=fn_survey_input_pl)
        # (II) remove participants who keep clicking the same answer or did not answer with X to a question
        d_filter_conditions = {lang.lstr(lang_db, "is_l1", category="column"):lang.lstr(lang_db, "yes", category="answer"), # match only if polish is L1
                               lang.lstr(lang_db, "is_l2", category="column"):lang.lstr(lang_db, "yes", category="answer"), # match only if english is L2
                               lang.lstr(lang_db, "how_often", category="column"):lang.lstr(lang_db, "often_daily", category="answer")} # match only if english is used daily
        means_en, means_pl = remove_participants(lang_db=lang_db,
                                                 means_en=means_en,
                                                 original_en=original_en,
                                                 means_pl=means_pl,
                                                 original_pl=original_pl,
                                                 d_filter_conditions=d_filter_conditions,
                                                 max_clicker_ratio=max_clicker_ratio)
        logging.info(f"processed english survey: {original_en.shape[0]} -> {means_en.shape[0]} participants")
        logging.info(f"processed polish survey: {original_pl.shape[0]} -> {means_pl.shape[0]} participants")
        # (III) save to means to csv in "./output"
        means_en = target.rename_index_to_participant(means_en) # start numbering from 1, rename index to "Participant"
        means_pl = target.rename_index_to_participant(means_pl) # start numbering from 1, rename index to "Participant"
        fm.save_dataframe_as_csv(obj=means_en, fn=fn_survey_output_en)
        fm.save_dataframe_as_csv(obj=means_pl, fn=fn_survey_output_pl)
    # otherwise, load csvs from output; this is useful if you want to edit them directly
    else:
        logging.info("ok: loading processed csvs from output because 'use_csv_from_input' is False")
        means_en = fm.load_csv(fn=fn_survey_output_en,
                               survey_lang="en")
        means_pl = fm.load_csv(fn=fn_survey_output_pl,
                               survey_lang="pl")
    if enabled["display_dataframes"] is True:
        logging.info(f"polish survey:\n{means_en}")
        logging.info(f"english survey:\n{means_pl}")
    return means_en, means_pl


def combine_dfs(means_en, means_pl, enabled):
    """
    combine two dataframes into one, put the 2nd below the 1st
    """
    # (1) combine into one dataframe
    means_both = pd.concat([means_en, means_pl], axis=0).fillna("")
    # (2) reset index numbering
    means_both.reset_index(inplace=True, drop=True)
    if enabled["display_dataframes"] is True:
        logging.info(f"combined survey:\n{means_both}")
    return means_both


def get_participants_statistics(lang_db, means_en, means_pl, enabled):
    """
    return dictionary with participants: age when began to learn english, age, gender, city size, uni year
    """
    r = dict()
    # (1) calculate participant size
    if enabled["get_participant_size"] is True:
        r.update({"participant size":{"english group":means_en.shape[0],
                                      "polish group":means_pl.shape[0]}})
    # (2) calculate when began to learn english
    if enabled["get_began_english"] is True:
        dict_learn_en = target.target_learn(means_en, lang.lstr(lang_db, "age_begin_eng", category="column"))
        dict_learn_pl = target.target_learn(means_pl, lang.lstr(lang_db, "age_begin_eng", category="column"))
        r.update({"en: began to learn":dict_learn_en,
                  "pl: began to learn":dict_learn_pl})
    # (3) calculate age
    if enabled["get_age"] is True:
        # df_both = pd.concat([means_en, means_pl], axis=0, ignore_index=True)
        # print(df_both)
        dict_age_en = target.target_age(means_en, lang.lstr(lang_db, "birth_year", category="column"))
        dict_age_pl = target.target_age(means_pl, lang.lstr(lang_db, "birth_year", category="column"))
        r.update({"en: age":dict_age_en,
                  "pl: age":dict_age_pl})
    # (4) calculate gender
    if enabled["get_gender"] is True:
        dict_gender_en = target.target_gender(means_en, lang.lstr(lang_db, "what_gender", category="column"))
        dict_gender_pl = target.target_gender(means_pl, lang.lstr(lang_db, "what_gender", category="column"))
        r.update({"en: gender":dict_gender_en,
                  "pl: gender":dict_gender_pl})
    # (5) calculate city size
    if enabled["get_city"] is True:
        dict_city_en = target.target_city(means_en, lang.lstr(lang_db, "how_big_city", category="column"))
        dict_city_pl = target.target_city(means_pl, lang.lstr(lang_db, "how_big_city", category="column"))
        r.update({"en: city size":dict_city_en,
                  "pl: city size":dict_city_pl})
    # (6) calculate uni year
    if enabled["get_uni_year"] is True:
        dict_uni_en = target.target_uni(means_en, lang.lstr(lang_db, "which_uni_year", category="column"))
        dict_uni_pl = target.target_uni(means_pl, lang.lstr(lang_db, "which_uni_year", category="column"))
        r.update({"en: uni year":dict_uni_en,
                  "pl: uni year":dict_uni_pl})
    logging.info("ok: calculated statistics for participants")
    return r
