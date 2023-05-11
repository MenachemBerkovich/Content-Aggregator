"""classes for Feed objects of a different types.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import contextlib
from typing import List, Tuple, Set
import time, datetime
from enum import Enum
import json

import feedparser
from bs4 import BeautifulSoup

from contentAggregator import config
from contentAggregator.sqlManagement import sqlQueries
from contentAggregator.feeds.rating import FeedRatingResetManager
from contentAggregator.common import ObjectResetOperationClassifier
from contentAggregator import webRequests


class FeedCategories(Enum):
    """Enum class for feed categories identification and detection"""

    NEWS = 0
    BLOGS = 1
    TECHNOLOGY = 2
    TRAVEL = 3


def match_category(category: FeedCategories) -> str:
    match category:
        case FeedCategories.NEWS:
            return config.FEEDS_CATEGORIES_NAMES.news
        case FeedCategories.BLOGS:
            return config.FEEDS_CATEGORIES_NAMES.blogs
        case FeedCategories.TECHNOLOGY:
            return config.FEEDS_CATEGORIES_NAMES.technology
        case FeedCategories.TRAVEL:
            return config.FEEDS_CATEGORIES_NAMES.travel


class Feed(ABC):
    """Represents a feed in the system.
    An half-abstract class for all feed types.
    """

    _instances = {}

    def __new__(cls, **kwargs) -> Feed:
        """Prevent instantiation of new feed with the same id as one that already exists
        in _instances dictionary.
        it's important to avoid unnecessary content downloads, for example.

        Returns:
            Feed: One of the feed types.
        """
        if "feed_id" not in kwargs:
            return super(Feed, cls).__new__(cls)
        if not cls._instances.get(kwargs["feed_id"], None):
            cls._instances[kwargs["feed_id"]] = super(Feed, cls).__new__(cls)
        return cls._instances[kwargs["feed_id"]]

    def __init__(self, *, feed_id: int) -> None:
        self._id = feed_id
        self._url: str | None = None
        self._rating: FeedRatingResetManager | None = None
        self._categories: Set[FeedCategories] | None = None
        self._content_info: Tuple[datetime.datetime, List[FeedItem]] | None = None
        self._parsed_feed: feedparser.FeedParserDict | str | None = None
        self._language: str | bool = None
        self._title: str | None = None
        self._image: str | bool = None
        self._website: str | bool = None
        self._description: str | bool = None

    def __repr__(self):
        return f"Feed(id={self._id})"

    def __str__(self):
        return f"""Feed object with id={self.id}
                and properties:
                url        = {self.url},
                rating    = {self.rating},
                """

    # Intended: for allowing management of feeds set without multiplications.
    def __eq__(self, other) -> bool:
        return self._id == other.id

    def __hash__(self) -> int:
        return hash(self._id)

    @property
    def id(self) -> int:
        """Property getter for feed id in the feeds table.

        Returns:
            int: The row id of this feed.
        """
        return self._id

    @property
    def url(self) -> str:
        """Property getter for this feed url.

        Returns:
            str: Feed url
        """
        if not self._url:
            self._url = sqlQueries.select(
                cols=config.FEEDS_DATA_COLUMNS.link,
                table=config.DATABASE_TABLES_NAMES.feeds_table,
                condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0][0]
        return self._url

    @url.setter
    def url(self, new_url: str) -> None:
        """Property setter for url of this feed.
        Necessary if url has changed.

        Args:
            new_url (str): The new url of this feed.

        Raises:
            ValueError: If url is invalid.
        """
        if not self.is_valid(new_url):
            raise ValueError("Invalid url")
        self._url = new_url
        sqlQueries.update(
            table=config.DATABASE_TABLES_NAMES.feeds_table,
            updates_dict={config.FEEDS_DATA_COLUMNS.link: new_url},
            condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self._id}",
        )

    @property
    def rating(self) -> float:
        """rating property getter.

        Returns:
            float: The rating of this feed.
        """
        if not self._rating:
            rating = sqlQueries.select(
                cols=config.FEEDS_DATA_COLUMNS.rating,
                table=config.DATABASE_TABLES_NAMES.feeds_table,
                condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0][0]
            self._rating = FeedRatingResetManager(rating)
        return self._rating.rating

    def _set_final_rating(self, rating_amount: float) -> float:
        """set the final rating of the feed,
        when it's setter is called with +=, -= or assignment operator.

        Args:
            rating_amount (float): The rating amount for calculate final rating by him.

        Returns:
            float: The final rating.
        """
        final_rating = rating_amount
        if self._rating.last_operation == ObjectResetOperationClassifier.ADDITION:
            final_rating = self.rating + rating_amount
        elif self._rating.last_operation == ObjectResetOperationClassifier.SUBTRACTION:
            final_rating = self.rating - rating_amount
        return final_rating

    @rating.setter
    def rating(self, rating_amount: float) -> None:
        """rating property setter.
        can be done with +=, -= or simple assignment (=).

        Args:
            rating_amount (float): The rating amount for reset the rating by him.

        Helper functions:
            _set_final_rating: Sets the final rating by the desired reset operation.
        """
        final_rating = self._set_final_rating(rating_amount)
        sqlQueries.update(
            table=config.DATABASE_TABLES_NAMES.feeds_table,
            updates_dict={config.FEEDS_DATA_COLUMNS.rating: final_rating},
            condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self.id}",
        )
        self._rating.rating = final_rating

    def should_be_updated(self) -> bool:
        """Checks if self.content_info needs to be updated.
           Depends on the last download time [if more than five minutes have passed]
           and if there was one.

        Returns:
            bool: True if feed should be updated, False otherwise.
        """
        return (
            not self._content_info
            or (self._content_info[0] - datetime.datetime.now()).seconds // 60 > 5
        )

    @property
    def categories(self) -> Set[str] | None:
        """Getter property, for categories of this feed.
        Each feed can cotains a lot of categories, like: news, technology,
        blogs and so on.

        Returns:
            Set[str] | None: A Set of categories if was defined, None otherwise.
        """
        if not self._categories:
            db_response = sqlQueries.select(
                cols=config.FEEDS_DATA_COLUMNS.categories,
                table=config.DATABASE_TABLES_NAMES.feeds_table,
                condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self._id}",
            )
            self._categories =  json.loads(db_response[0][0])
        return {match_category(category) for category in self._categories}

    @categories.setter
    def categories(self, *categories: FeedCategories) -> None:
        """Setter for the feed categories.
        will be update the database and self._categories.
        
        Args:
            categories (FeedCategories): a variable number of arguments, from the Enum class FeedCategories.
        """
        if any(not isinstance(category, FeedCategories) for category in categories):
            raise ValueError("Feed category must be a type of FeedCategories Enum class.")
        new_categories = set(categories)
        sqlQueries.update(
            table=config.DATABASE_TABLES_NAMES.feeds_table,
            updates_dict={
                config.FEEDS_DATA_COLUMNS.categories: json.dumps(new_categories)
            },
            condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {self._id}",
        )
        self._categories = new_categories

    @abstractmethod
    @property
    def language(self) -> str | bool:
        """Getter property of the feed language.

        Returns:
            str | bool: The feed language as a string if available, False otherwise.
        """
        pass
        #TODO concrete classes


    @property
    @abstractmethod
    def title(self) -> str:
        """Returns the feed name \ title.

        Returns:
            str: title if available, name [extracted from self.url].
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str | bool:
        """Returns the description of the feed if available.

        Returns:
            str  | bool: The description if available, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def image(self) -> str | bool:
        """Returns the feed image url if available.

        Returns:
            str | None: url str if available, None otherwise.
        """
        pass

    @property
    def content(self) -> List[FeedItem]:
        """Property for the feed content,
        which is a list of FeedItem objects.

        Returns:
            List[FeedItem]: The list of feed items.
        """
        self.ensure_updated_stream()
        return self._content_info[1]

    @property
    @abstractmethod
    def website(self) -> str | bool:
        """Returns the website url of the feed, if available"""
        pass

    @staticmethod
    @abstractmethod
    def is_valid(url: str) -> bool:
        """Abstract method to check if a url is valid
        depending on its type.
        """
        pass

    def _download(self) -> str:
        """Downloads the feed content.

        Returns:
            str: Feed content.
        """
        return webRequests.get_response(method="get", url=self._url).text

    @abstractmethod
    def ensure_updated_stream(self) -> None:
        """Ensures that the feed is updated per five minutes."""
        pass


class XMLFeed(Feed):
    """Concrete class for based-XML feeds, such as RSS, CDF and Atom,
    with specific implementation for is_valid function.
    """

    @staticmethod
    def is_valid(url: str) -> bool:
        """static method to check whether the given url is valid for RSS feeds or not.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the url is valid, False otherwise.
        """
        with contextlib.suppress(Exception):
            feed = feedparser.parse(url)
            if feed.version:
                return True
        return False

    def ensure_updated_stream(self) -> None:
        if self.should_be_updated():
            self._parsed_feed = feedparser.parse(self._download())
            self._content_info = datetime.datetime.now(), [
                XMLFeedItem(item, self._parsed_feed.version)
                for item in self._parsed_feed.entries
            ]

    @property
    def title(self) -> str:
        if not self._title:
            try:
                self._title = self._parsed_feed.channel.title
            except KeyError:
                self._title = self.url[self.url.find("//") + 2 : self.url.find(".")]
        return self._title

    @property
    def description(self) -> str | bool:
        if self._description is None:
            try:
                self._description = self._parsed_feed.channel.description
            except KeyError:
                self._description = False
        return self._description

    @property
    def image(self) -> str | bool:
        self.ensure_updated_stream()
        if self._image is None:
            try:
                self._image = self._parsed_feed.channel.image.href
            except KeyError:
                self._image = False
        return self._image

    @property
    def website(self) -> str | bool:
        if self._website is None:
            try:
                self._website = self._parsed_feed.channel.link
            except KeyError:
                self._website = False
        return self._website


class HTMLFeed(Feed):
    """Concrete class for HTML feeds,
    with specific implementation for is_valid function.
    """

    @staticmethod
    def is_valid(url: str) -> bool:
        """static method to check whether the given url is valid for HTML feeds or not.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the url is valid, False otherwise.
        """
        return (
            webRequests.get_response(method="head", url=url).headers["content-type"]
            == "text/html"
        )


class FeedFactory:
    """Factory for creating a custom feed object by url parameter"""

    @staticmethod
    def create(feed_id: int) -> Feed:
        """Creates a feed object by its type.

        Args:
            feed_id (int): The id of the feed.

        Returns:
            Feed: An Feed object matched to the feed type.

        """
        feed_type = sqlQueries.select(
            cols=config.FEEDS_DATA_COLUMNS.feed_type,
            table=config.DATABASE_TABLES_NAMES.feeds_table,
            condition_expr=f"{config.FEEDS_DATA_COLUMNS.id} = {feed_id}",
        )[0][0]
        match feed_type:
            case config.FEED_TYPES.html:
                return HTMLFeed(feed_id=feed_id)
            case config.FEED_TYPES.xml:
                return XMLFeed(feed_id=feed_id)


class FeedItem(ABC):
    """Represents a feed item, with link, image, title, and publication_time attributes.
    FeedItem can be a news item, a podcast item, or anything like that.
    """

    def __init__(
        self, item_string: feedparser.util.FeedParserDict, feed_version: str
    ) -> None:
        self._item: feedparser.util.FeedParserDict = item_string
        self._version: str = feed_version
        self._image: str | bool = None
        self._title: str | bool = None
        self._description: str | bool = None
        self._url: str | bool = None
        self._publication_time: time.struct_time | bool = None

    @property
    @abstractmethod
    def image(self) -> str | bool:
        """Returns the url of the image describes this item, if there is one.

        Returns:
            str | bool: The image url if available, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Returns the title \ header of the item.

        Returns:
            str: The title of the item as string.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str | bool:
        """Returns the description of the item, if available. else returns False"""
        pass

    @property
    @abstractmethod
    def url(self) -> str:
        """Returns the specific url of this item.

        Returns:
            str: The url of the item.
        """
        pass

    @property
    @abstractmethod
    def publication_time(self) -> time.struct_time | bool:
        """Returns the publication date and time of the item.

        Returns:
            datetime | bool: The publication date and time of the item if available, false otherwise.
        """
        pass


class XMLFeedItem(FeedItem):
    """Construct of a feed item.
    contains the feed properties, with easy and secure access.
    """

    @property
    def image(self) -> str | bool:
        if "rss2" not in self._version:
            self._image = False
        if self._image is None:
            try:
                self._image = self._item.media_thumbnail[0]["url"]
            except KeyError:
                self._image = False
        return self._image

    @property
    def title(self) -> str | bool:
        if self._title is None:
            try:
                self._title = self._item.title
            except KeyError:
                self._title = False
        return self._title

    @property
    def description(self) -> str | bool:
        if self._description is None:
            try:
                description = self._item.description
                description_soup = BeautifulSoup(description, "html.parser")
                if description_str := description_soup.find("a"):
                    self._description = description_str.text.strip()
                else:
                    self._description = description
            except KeyError:
                self._description = False
        return self._description

    @property
    def url(self) -> str | bool:
        if not self._url:
            try:
                self._url = self._item.link
            except KeyError:
                self._url = False
        return self._url

    @property
    def publication_time(self) -> time.struct_time | bool:
        if self._publication_time is None:
            try:
                self._publication_time = self._item.updated_parsed
            except KeyError:
                self._publication_time = False
        return self._publication_time
