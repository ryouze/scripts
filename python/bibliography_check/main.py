"""main function"""
import file_manager
import logging
import sys
import web


def main():
    # purge log file
    open("log.log", "w").close()
    # setup logger
    logging.basicConfig(datefmt="%G-%m-%d %T",
                        format="%(asctime)s [%(levelname)s] %(module)s.py : %(funcName)s() - %(message)s",
                        encoding="utf-8",
                        handlers=[logging.FileHandler("./log.log"), logging.StreamHandler(sys.stdout)],
                        level=logging.DEBUG)
    # download a list of predatory scholarly open-access publishers
    list_publishers = web.get_publishers("https://beallslist.net/")
    # load txt file contaning your bibliography
    # print(wtf)
    my_bibliography = file_manager.load_file("./input/your_bibliography.txt")
    # compare each bibliography against list of known publishers
    r = list()
    for line in my_bibliography:
        logging.debug(f"checking bibliograhy: {line}")
        for publisher in list_publishers:
            if publisher in line:
                logging.info(f"predatory publisher '{publisher}' found in: {line}")
                r.append(f"publisher '{publisher}' found in bibliography: {line}")
    # print results
    full_string = "*" * 60 + "\n--- list of potentailly predatory publishers found in your bibliography ---\n" + "\n".join(r)
    logging.info(full_string)
    logging.info("program exist")
    return


if __name__ == "__main__":
    main()
