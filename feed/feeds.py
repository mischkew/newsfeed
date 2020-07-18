import logging
from pprint import pformat

from bs4 import BeautifulSoup

from ..feed import Feed


def parser(dom: BeautifulSoup) -> str:
    latest_chapter_link = dom.select(
        "#Chapters_List .ceo_latest_comics_widget li:first-child a"
    )[0]

    logging.debug(pformat(latest_chapter_link, indent=2))
    return str(latest_chapter_link)


def build_email(title: str, dom: BeautifulSoup) -> str:
    email = f"A new chapter of {title} is available!\n"
    email += str(dom)
    return email


OnePunchManFeed = Feed(
    title="One Punch Man",
    url="https://ldkmanga.com",
    parser=parser,
    build_email=build_email,
)
OnePieceFeed = Feed(
    title="One Piece",
    url="https://onepiece-mangaonline.com/",
    parser=parser,
    build_email=build_email,
)

FEEDS = sorted([OnePunchManFeed, OnePieceFeed], key=lambda f: f.title)
