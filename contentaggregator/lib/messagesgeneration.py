"""This module contains a several functions,
which intended to generate messages in several forms, for various destinations
such as Email, whatsapp, voice messages, etc.
"""
from typing import List
import time

import tinyhtml

from contentaggregator.lib import config
from contentaggregator.lib.feeds.feed import Feed, FeedItem


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


def generate_html_feed_summery(feed: Feed) -> str:
    """Generates a prettify HTML string for specific given feed.

    Args:
        feed (Feed): A feed to be extract from.

    Returns:
        str: The html string.
    """
    feed_content = feed.content
    _sort_feed_items(feed_content)
    html_obj = tinyhtml.h("div", style="text-align: center;")(
        #Place the website image or trademark on the top of the summary.
        (
            tinyhtml.h("a", href=feed.website)(
                tinyhtml.h("img", src=feed.image) if feed.image else None
            )
            if feed.website
            else None
        ),
        #Below, place the name of the feed.
        (tinyhtml.h("h1")(feed.title) if feed.title else None),
        *(
            #Now, below, place the feed items, item by item.
            tinyhtml.h("h2")(
                (
                    tinyhtml.h("div", style="font-size: 15px;")(
                        time.strftime("%d/%m/%Y %H:%M", item.publication_time)
                        if item.publication_time
                        else ""
                    )
                ),
                tinyhtml.h("a", href=item.url)(
                    f"{item.title}" if item.title else f"{item.description}"
                ),
                (tinyhtml.h("h3")(item.description if item.title else "")),
                (
                    tinyhtml.h(
                        "img", src=item.image, style="max-width: 50%;max-height: 50%"
                    )
                    if item.image
                    else ""
                ),
            )
            for item in feed_content
        ),
    )
    return html_obj.render()
