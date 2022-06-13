"""main function (5)"""
from time import perf_counter
import comp
import fm
import logging
import sys
import target


def main():
    """
    main function
    """
    # start counting time
    start_time = perf_counter()
    # purge log file
    open("./log.log", "w").close()
    # setup logger
    logging.basicConfig(datefmt="%G-%m-%d %T",
                        format="%(asctime)s [%(levelname)s] %(module)s.py : %(funcName)s() - %(message)s",
                        encoding="utf-8",
                        handlers=[logging.FileHandler("./log.log"), logging.StreamHandler(sys.stdout)],
                        level=logging.INFO)
    # (0) user toggles
    enabled = {"use_csv_from_input":True, # if false then csv from "./output" will be loaded
               # useful if you want to edit them manually and then pass them to get_participants_statistics()
               "display_dataframes":True, # if false then dataframes won't be printed out
               "get_participant_size":True,
               "get_began_english":True,
               "get_age":True,
               "get_gender":True,
               "get_city":True,
               "get_uni_year":True}
    # (1) load language database: english/polish language database of column names and answers
    lang_db = fm.load_json(fn="./input/lang_db.json")
    # (2) load custom column names for questions
    colls_db = fm.load_columns(fn="./input/column_names.txt")
    # (3) load csvs, save a copy to "./output"
    means_en, means_pl = comp.get_clean_dfs(lang_db=lang_db,
                                            enabled=enabled,
                                            colls_db=colls_db,
                                            fn_survey_input_en="./input/Survey research EN.csv",
                                            fn_survey_input_pl="./input/Survey research PL.csv",
                                            fn_survey_output_en="./output/processed_EN.csv",
                                            fn_survey_output_pl="./output/processed_PL.csv",
                                            max_clicker_ratio=80)
    # (4) combine both dataframes into one
    means_both = comp.combine_dfs(means_en=means_en,
                                  means_pl=means_pl,
                                  enabled=enabled)
    means_both = target.rename_index_to_participant(means_both) # start numbering from 1, rename index to "Participant"
    # (5) calculate statistics (e.g., age, gender, city size):
    stats = comp.get_participants_statistics(lang_db=lang_db,
                                             means_en=means_en,
                                             means_pl=means_pl,
                                             enabled=enabled)
    # (6) save all columns in combined means to csv
    fm.save_dataframe_as_csv(obj=means_both,
                             fn="./output/combined_all_columns.csv")
    # (7) save only mean values + "Language" column to csv
    colls = list(set(colls_db))
    colls.insert(0, "Language")
    means_both = means_both.filter(colls)
    fm.save_dataframe_as_csv(obj=means_both,
                             fn="./output/combined_means_only.csv")
    # (8) save participants statistics to a txt file
    fm.save_dictionary_as_txt(obj=stats,
                              header="[all data below has been calculated after the participants were removed]",
                              fn="./output/stats.txt")
    logging.info(f'program ended, took {round(perf_counter() - start_time, 3)} seconds')
    return


if __name__ == "__main__":
    main()
