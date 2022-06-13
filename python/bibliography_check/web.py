"""download a list of predatory publishers"""
from bs4 import BeautifulSoup
import logging
import requests


# setup per-module logger
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def download_website(link, encoding="utf-8", timeout=10):
    """
    download a website and return its content as string
    """
    # send a GET request to website and receive its content
    logging.debug(f"trying to download website: {link}; timeout={timeout} seconds")
    try:
        r = requests.get(link, timeout=timeout)
    except Exception as e:
        logging.error(f"failed to download website '{link}', reason: {e}")
        raise
    # if custom encoding was provided, encode it
    if encoding:
        logging.debug(f"converting to custom encoding: {encoding} ")
        r.encoding = encoding
    # convert to text
    r = r.text
    logging.info(f"ok: downloaded website ({len(r)} characters): {link}")
    return r


def create_soup(html_content):
    """
    create bs4 soup object using html content
    """
    try:
        # create soup class
        soup = BeautifulSoup(html_content, features="html.parser")
        logging.debug(f"created soup object for website: {soup.title.text}")
    except Exception as e:
        logging.error(f"failed to create soup object; reason: {e}")
        raise
    return soup


def get_publishers(link, encoding="utf-8", timeout=10):
    """

    """
    # define list of publishers that will be returned
    r = list()
    # download website: list of publishers
    html = download_website(link, encoding=encoding, timeout=timeout)
    # create bs4 soup object
    soup = create_soup(html)
    # select main div containing article
    main_div = soup.find("div", attrs={"class": "wp-block-column", "style": "flex-basis: 75%;"})
    if main_div is None:
        logging.error("failed to find main div containing article")
        raise
    # get first unordered list
    ulist = main_div.find("ul")
    if ulist is None:
        logging.error("failed to find unordered list within main div containing article")
        raise
    # get all publishers
    for item in ulist.find_all("li"):
        try:
            link = item.find("a", href=True).text
        # if no link present, get just the text within tag (some publishers are not hyperlinked)
        except AttributeError:
            link = item.text
        # append publisher to link
        r.append(link)
        continue
    logging.info(f"ok: downloaded a list of {len(r)} predatory publishers")
    return r
