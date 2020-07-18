import logging
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

USER_AGENT = "Feed v1.0.0"

Parser = Callable[[BeautifulSoup], str]


def parse_domain(url: str) -> str:
    return urlparse(url).netloc


def request(url: str) -> str:
    """Request an HTTP/ HTTPS webpage and return its body. Automatically sets
    the `HOST` header based on the url's domain name and assigns the app's user
    agent.
    """
    domain = parse_domain(url)
    request = Request(url, headers={"HOST": domain, "User-Agent": USER_AGENT})
    with urlopen(request) as response:
        content = response.read().decode("utf8")
        return content


def fetch(url: str, parser: Parser) -> str:
    logging.debug(f"Fetch url: {url}")
    content = request(url)
    document = BeautifulSoup(content, "html.parser")
    return parser(document)


def store(content: str, path: Path) -> None:
    path.write_text(content, "utf8")


def read(path: Path) -> str:
    return path.read_text("utf8")
