import logging
from pprint import pformat
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .feed import Feed, Parser, MailBuilder


class DuplicateFeed(Exception):
    pass


class NoAnchorTag(Exception):
    pass


def ensure_no_duplicates(feeds) -> None:
    seen = set()
    for feed in feeds:
        if feed.id in seen:
            raise DuplicateFeed(f"The feed {feed.title} is already defined!")
        seen.add(feed.id)


BLOG_POST_EMAIL = "A new blog post of {title} is available!"
MANGA_CHAPTER_EMAIL = "A new chapter of {title} is available!"
EPISODE_EMAIL = "A new episode of {title} is available!"


def build_parser(pattern: str) -> Parser:
    """Create a parser from a CSS selector. If the selector returns multiple
    elements, only the first one is observed for change. The CSS selector should
    contain a link.
    """

    def parser(feed: Feed, dom: BeautifulSoup) -> str:
        element = dom.select(pattern)[0]
        logging.debug(pformat(element, indent=2))

        if element.name != "a" and element.find("a") is None:
            raise NoAnchorTag("The parser pattern must contain an anchor-tag!")

        return str(element)

    return parser


def build_mail_builder(prefix: str) -> MailBuilder:
    """Creates an email builder from a text which is prepended to the parsed DOM
    element. If the parsed DOM element is a relative link, the domain url will
    be prepended to convert it into an absolute link (which can be visited from
    the email client of the recipient).
    """

    def mail_builder(feed: Feed, dom: BeautifulSoup) -> str:
        link = dom.select("a")[0]
        link["href"] = urljoin(feed.url, link["href"])

        email = prefix.format(**feed._asdict())
        email += "\n"
        email += str(dom)
        return email

    return mail_builder


OnePunchManFeed = Feed(
    title="One Punch Man",
    url="https://ldkmanga.com",
    parser=build_parser("#Chapters_List .ceo_latest_comics_widget li:first-child a"),
    build_email=build_mail_builder(MANGA_CHAPTER_EMAIL),
)
OnePieceFeed = Feed(
    title="One Piece",
    url="https://onepiece-mangaonline.com/",
    parser=build_parser("#Chapters_List .ceo_latest_comics_widget li:first-child a"),
    build_email=build_mail_builder(MANGA_CHAPTER_EMAIL),
)
CleanCodeFeed = Feed(
    title="Clean Code Blog",
    url="https://blog.cleancoder.com/",
    parser=build_parser("aside ul li:first-child a"),
    build_email=build_mail_builder(BLOG_POST_EMAIL),
)
HinowaGaYukuFeed = Feed(
    title="Hinowa Ga Yuku",
    url="https://mangakakalot.com/read-lt3yx158504948647",
    parser=build_parser("#chapter .chapter-list .row:first-child a"),
    build_email=build_mail_builder(MANGA_CHAPTER_EMAIL),
)
EnenNoShouboutai = Feed(
    title="Enen No Shouboutai Season 2",
    url="https://www11.gogoanimehub.com/enen-no-shouboutai-ni-no-shou-episode-1-1",
    parser=build_parser(".episodes li:first-child a"),
    build_email=build_mail_builder(EPISODE_EMAIL),
)

FEEDS = sorted(
    [OnePunchManFeed, OnePieceFeed, CleanCodeFeed, HinowaGaYukuFeed, EnenNoShouboutai],
    key=lambda f: f.id,
)
FEED_ID_INDEX = {feed.id: feed for feed in FEEDS}
ensure_no_duplicates(FEEDS)


def get_feeds_from_ids(ids: List[str]) -> List[Feed]:
    return [FEED_ID_INDEX[feed_id] for feed_id in ids]
