from typing import Dict, List

from .feed import Feed, build_feed


class DuplicateFeed(Exception):
    pass


class Registry:
    def __init__(self):
        self.feeds: Dict[str, Feed] = {}

    def has_feed_with_id(self, feed_id: str) -> bool:
        return feed_id in self.feeds

    def add_feed(self, feed: Feed) -> None:
        if self.has_feed_with_id(feed.id):
            raise DuplicateFeed(f"The feed {feed.title} is already defined!")

        self.feeds[feed.id] = feed

    def register_feed(
        self, title: str, url: str, selector: str, email_body: str
    ) -> None:
        feed = build_feed(title, url, selector, email_body)
        self.add_feed(feed)

    def get_feeds(self) -> List[Feed]:
        return self.feeds.values()

    def get_feeds_from_ids(self, ids: List[str]) -> List[Feed]:
        return [self.feeds[feed_id] for feed_id in ids]
