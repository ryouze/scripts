"""
Main function.
"""
from proc import calculate_main
from time import perf_counter
import logging
import sys


def main():
    """
    Main function.
    Requires bs4: pip install beautifulsoup4
    """
    start_time = perf_counter()
    # purge log file
    open("./log.log", "w").close()
    # setup logger - print to console and write to "log.log"
    logging.basicConfig(datefmt="%G-%m-%d %T",
                        format="%(asctime)s [%(levelname)s] %(module)s.py : %(funcName)s() - %(message)s",
                        encoding="utf-8",
                        handlers=[logging.FileHandler("./log.log"), logging.StreamHandler(sys.stdout)],
                        level=logging.INFO)
    calculate_main(input="./my_grades.html",
                   output="./output.txt")
    logging.info(f'program ended, took {round(perf_counter() - start_time, 3)} seconds')
    return


if __name__ == "__main__":
    main()
