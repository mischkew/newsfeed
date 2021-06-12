import logging
import os
from pathlib import Path
from pprint import pformat
from typing import Callable, NamedTuple, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .email import FeedMailer
from .scrape import Parser, fetch, read, store

DEFAULT_CACHE_DIR = "./.feed_cache"
CUSTOM_CACHE_DIR: Optional[Path] = None


def get_cache_dir() -> Path:
    if CUSTOM_CACHE_DIR:
        return CUSTOM_CACHE_DIR
    return Path(os.environ.get("FEED_CACHE_DIR", DEFAULT_CACHE_DIR))


def set_cache_dir(path: Path) -> None:
    if not path.is_dir():
        raise FileNotFoundError(f"The directory cache path {path} does not exist!")

    global CUSTOM_CACHE_DIR
    CUSTOM_CACHE_DIR = path


def slugify(text: str) -> str:
    """Remove whitespace from text, join words with a hyphen and make the
    string all lowercase.
    """
    return text.strip().replace(" ", "-").lower()


def diff_and_update(
    content: str, cached_content_path: Path, differ_on_create=True, should_update=True
) -> bool:
    """Compare string-based content with already cached content on disk.
    Updates the cached content if the current content is different and if
    should_update is True. Returns True, if the contents differ. If
    differ_on_create is False, does not return True, if the cached_content is
    created for the first time.
    """
    cached_content = None
    if cached_content_path.is_file():
        cached_content = read(cached_content_path)

    if content != cached_content:
        if should_update:
            store(content, cached_content_path)
        return differ_on_create

    return False


MailBuilder = Callable[[str, BeautifulSoup], str]


class Feed(NamedTuple):
    title: str
    url: str
    parser: Parser
    build_email: MailBuilder

    @property
    def id(self):
        return slugify(self.title)

    @property
    def path(self):
        cache_dir = get_cache_dir()
        path = (cache_dir / self.id).with_suffix(".html")
        return path

    def sync(self, differ_on_create=True, dry_run=False) -> FeedMailer:
        logging.info(f"Syncing feed {self.title}")
        dom = fetch(self.url)
        content = self.parser(self, dom)

        is_different = diff_and_update(
            content, self.path, differ_on_create, should_update=not dry_run
        )
        logging.debug(f"Feed {self.title} is different: {is_different}")

        return FeedMailer(
            subject=self.title,
            should_send=is_different,
            email=self.build_email(self, BeautifulSoup(content, "html.parser")),
        )


class NoAnchorTag(Exception):
    pass


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


def build_feed(title: str, url: str, selector: str, email_body: str) -> Feed:
    """A convenience method to construct feeds from CSS-selector and email body
    strings.
    """
    return Feed(
        title=title,
        url=url,
        parser=build_parser(selector),
        build_email=build_mail_builder(email_body),
    )
