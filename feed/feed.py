# fetch webpage from link
# diff with cached local previous fetch
# if no previous fetch or different,
#   prepare email body with new chapter link
#   send email to recepient

# provides:
# - weblink
# - parse pattern for diffing
# - method for assembling email body

# defines a feed per relevant website

# - one punch man
# - one piece
import logging
import os
from pathlib import Path
from typing import Callable, NamedTuple, Optional

from bs4 import BeautifulSoup

from .email import FeedMailer
from .scrape import Parser, fetch, read, store

DEFAULT_CACHE_DIR = "./.feed_cache"
CUSTOM_CACHE_DIR: Optional[Path] = None


def get_cache_dir() -> Path:
    if CUSTOM_CACHE_DIR:
        return CUSTOM_CACHE_DIR
    return Path(os.environ.get("FEED_CACHE_PATH", DEFAULT_CACHE_DIR))


def set_cache_path(path: Path) -> None:
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
    content: str, cached_content_path: Path, differ_on_create=True
) -> bool:
    """Compare string-based content with already cached content on disk.
    Updates the cached content if the current content is different. Returns
    True, if the contents differ. If differ_on_create is False, does not
    return True, if the cached_content is created for the first time.
    """
    cached_content = None
    if cached_content_path.is_file():
        cached_content = read(cached_content_path)

    if content != cached_content:
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
    def path(self):
        cache_dir = get_cache_dir()
        path = (cache_dir / slugify(self.title)).with_suffix(".html")
        return path

    def sync(self, differ_on_create=True) -> FeedMailer:
        logging.info(f"Syncing feed {self.title}")
        content = fetch(self.url, self.parser)

        is_different = diff_and_update(content, self.path, differ_on_create)
        logging.debug(f"Feed {self.title} is different: {is_different}")

        return FeedMailer(
            feed=self,
            should_send=is_different,
            email=self.build_email(self.title, BeautifulSoup(content, "html.parser")),
        )
