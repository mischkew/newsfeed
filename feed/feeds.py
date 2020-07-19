import logging
from pprint import pformat
from typing import List

from bs4 import BeautifulSoup

from .feed import Feed


class DuplicateFeed(Exception):
    pass


def ensure_no_duplicates(feeds) -> None:
    seen = set()
    for feed in feeds:
        if feed.id in seen:
            raise DuplicateFeed(f"The feed {feed.title} is already defined!")
        seen.add(feed.id)


def manga_parser(feed: Feed, dom: BeautifulSoup) -> str:
    latest_chapter_link = dom.select(
        "#Chapters_List .ceo_latest_comics_widget li:first-child a"
    )[0]

    logging.debug(pformat(latest_chapter_link, indent=2))
    return str(latest_chapter_link)


def build_manga_email(feed: Feed, dom: BeautifulSoup) -> str:
    email = f"A new chapter of {feed.title} is available!\n"
    email += str(dom)
    return email


def clean_code_parser(feed: Feed, dom: BeautifulSoup) -> str:
    latest_post = dom.select("aside ul li:first-child a")[0]

    logging.debug(pformat(latest_post, indent=2))
    return str(latest_post)


def build_clean_code_email(feed: Feed, dom: BeautifulSoup) -> str:
    # uncle bob's blog uses relative links, so we prepend the webpage url
    link = dom.select("a")[0]
    link["href"] = feed.url + link["href"]

    email = f"A new blog post of {feed.title} is available!\n"
    email += str(link)
    return email


OnePunchManFeed = Feed(
    title="One Punch Man",
    url="https://ldkmanga.com",
    parser=manga_parser,
    build_email=build_manga_email,
)
OnePieceFeed = Feed(
    title="One Piece",
    url="https://onepiece-mangaonline.com/",
    parser=manga_parser,
    build_email=build_manga_email,
)
CleanCodeFeed = Feed(
    title="Clean Code Blog",
    url="https://blog.cleancoder.com/",
    parser=clean_code_parser,
    build_email=build_clean_code_email,
)

FEEDS = sorted([OnePunchManFeed, OnePieceFeed, CleanCodeFeed], key=lambda f: f.id)
FEED_ID_INDEX = {feed.id: feed for feed in FEEDS}
ensure_no_duplicates(FEEDS)


def get_feeds_from_ids(ids: List[str]) -> List[Feed]:
    return [FEED_ID_INDEX[feed_id] for feed_id in ids]
