"""Extract grades from HTML file."""
from bs4 import BeautifulSoup
import logging

# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_html(filename, encoding="utf-8"):
    """
    Load HTML from filename.
    """
    with open(filename, "r", encoding=encoding) as file:
        r = file.read()
    logging.info(f"loaded html file: '{filename}'")
    return r


def create_soup(html_content):
    """
    Create bs4 soup object using html content.
    """
    try:
        # create soup class
        soup = BeautifulSoup(html_content, features="html.parser")
        title = soup.title.text
        logging.debug(f"created soup object for website: {title}")
    except Exception as e:
        logging.error(f"failed to create soup object; reason: {e}")
        raise Exception("failed to create soup object")
    return soup


def get_grades_from_table(table_content):
    """
    Return overall average grade and a dictionary, where key is semester and value is a list of grades, with subject as first line.
    """
    # total average grade over the years, will be turned into float at end
    total_avg_grade = list()
    # subjects and grades that will be returned
    r = dict()
    # set title that will be updated when moving down the table
    current_title = str()
    # for each table row
    for row in table_content.find_all("tr"):
        # get all columns
        column = row.find_all("td")
        # get total amount of columns for current row (e.g., 4)
        column_length = len(column)
        # if 1 column then set semester title (e.g., Academic year 2019/2020)
        if column_length == 1:
            # get its text without html tags
            current_title = column[0].get_text(separator="")
            # remove newlines and trailing text
            current_title = current_title.replace("\n", " ").strip()
            # remove "- hide at the end"; now the current title is set till next loop overwrites it
            current_title = current_title[:-7]
            logging.debug(f"set semester title: '{current_title}'")
        # if 4 columns then grade, get third column because it contains grade (counts from zero, so: 0, 1, 2, 3)
        elif column_length == 4:
            # pre-check: make sure semester title is not empty (should never happen)
            if len(current_title) < 3:
                logging.error(f"found grade but semester title is not available, skipping current grade: {current_title}")
                continue
            # get text of subject
            subject = column[0].a.text #.get_text(separator="")
            # get list of grades for that subject
            grade_list = column[2].find_all("span")
            # convert content of list of grades to text, turn polish decimals to american decimals
            grade_list = [i.text.replace(",", ".") for i in grade_list]
            # temporarily convert to floats, so we can try to calculate average at the end, and maybe now too if multiple grades present
            try:
                # remove parenthesized from float calculation, it's either a grade that had been changed after a retake (e.g., (2) -> 4) or some string
                temp = [float(i) for i in grade_list if i[0] != "z" and i[0] != "("]
                # append to total average grade list
                total_avg_grade += temp
                # calculate average and append it to subject string
                if len(grade_list) > 1:
                    logging.debug(f"multiple grades detected, trying to calculate average: {grade_list}")
                    avg = sum(temp) / len(temp)
                    logging.debug(f"succeeded in getting average of {grade_list}, result is: {avg}")
                    subject = f"{subject} | average: {round(avg, 2)}"
            except Exception:
                logging.warning(f"failed to convert to float, leaving as-is: {grade_list}")
            # add asterisk at the beggining
            grade_list = ["* " + i for i in grade_list]
            # create string that will be saved as value
            full_grade = f"[{subject}]\n" + "\n".join(grade_list)
            logging.debug(f"column '{current_title}' has grade: '{full_grade}'")
            # if key doesn't already exist, create key (string) and value (list)
            if current_title not in r:
                r[current_title] = [full_grade]
            else:
                # otherwise, add to it
                r[current_title] += [full_grade]
        continue
    # check if list not empty
    if not total_avg_grade:
        logging.critical("zero grades were extracted, quitting program; please check if titles of semesters are available")
        quit()
    # calculate overall grade
    total_avg_grade = round(sum(total_avg_grade) / len(total_avg_grade), 2)
    logging.info(f"processed grades and calculcated avg grade: {total_avg_grade}")
    return total_avg_grade, r


def save_dictionary_to_txt(obj, avg, filename, encoding="utf-8"):
    """
    Save dictionary to a txt as a string in the following format:
    [Total average grade overall: int]


    [KEY]
    * LIST_ITEM_1
    * LIST_ITEM_1


    [KEY2]
    * LIST_ITEM_1
    * LIST_ITEM_1
    """
    string_to_save = f"Total average grade overall: {avg}"
    for semester, subject_and_grades in obj.items():
        current_block = f"## {semester} ##\n" + "\n".join(subject_and_grades)
        logging.debug(f"created block using key: {current_block}")
        # append to string, with two newlines between each block
        string_to_save += "\n\n\n" + current_block
    # add newline at the end
    string_to_save += "\n"
    # save long string to txt file
    with open(filename, "w", encoding=encoding) as file:
        file.write(string_to_save)
    logging.info(f"saved grades to: {filename}")
    return


def calculate_main(input, output):
    """
    Load grades from an offline copy of USOS.
    Save results to output.txt.
    """
    # load html from html file
    html = load_html(input)
    # create bs4 object
    soup = create_soup(html)
    # find table containing grades
    table_grades = soup.find("table", {"class": "grey"})
    # get average grade and dictionary of grades by semester
    avg_grade, grades_dict = get_grades_from_table(table_grades)
    # save grades to txt file
    save_dictionary_to_txt(grades_dict, avg_grade, output)
    return
