# command line tool to call update for all or selected subset of feeds
# - dry-run option
# - recepient email
# - sender email
#   if credentials in environment variables, then use, otherwise ask on CLI with
#   secret input for password
# - path for storing diff files
# - option to not send email on initial crawl
# - option to attach remote debugger
# command to clear diff files
import logging
from pprint import pformat

from bs4 import BeautifulSoup

from .feed import Feed


def parser(dom: BeautifulSoup) -> str:
    latest_chapter_link = dom.select(
        "#Chapters_List .ceo_latest_comics_widget li:first-child a"
    )[0]

    logging.debug(pformat(latest_chapter_link, indent=2))
    return str(latest_chapter_link)

    # def to_email(dom: BeautifulSoup) -> str:
    #     raise NotImplementedError


def main():
    OnePunchManFeed = Feed(
        title="One Punch Man", url="https://ldkmanga.com", parser=parser
    )
    OnePunchManFeed.sync_and_send()
