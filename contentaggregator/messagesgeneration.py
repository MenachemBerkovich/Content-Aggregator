"""This module contains a several functions,
which intended to generate messages in several forms, for various destinations such as Email, whatsapp, voice messages, etc.
"""
from typing import List

import tinyhtml

from contentaggregator import config
from contentaggregator.feeds.feed import Feed, FeedItem


def _sort_feed_items(feed_items: List[FeedItem]) -> None:
    """Sorts items in-place by it's publishing date if it's available, in a reverse order

    Args:
        feed_items (List[FeedItem]): List of feed items.
    """
    if all(item.publication_time for item in feed_items):
        feed_items.sort(
            key=lambda x: (
                x.publication_time.tm_year,
                x.publication_time.tm_mon,
                x.publication_time.tm_mday,
                x.publication_time.tm_hour,
                x.publication_time.tm_min,
            ),
            reverse=True,
        )


def generate_html_message(*feeds: Feed) -> str:
    """Generates a message from collection of feeds, to a pretify html message.

    Args:
        feeds (Feed): Variable number of feeds objects, to be extract from.

    Returns:
        str: The html string.
    """
    html_obj = tinyhtml.html()
    html_obj(tinyhtml.h('div', style="text-align: center;"))
    html_obj(tinyhtml.h('h1', ))
    for feed in feeds:
        content = feed.content
        _sort_feed_items(content)
        for item in content:
            pass
            
        
