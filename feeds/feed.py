"""classes for Feed objects of a different types.
"""


from abc import ABC, abstractmethod
import contextlib

import feedparser

import config
from sqlManagement import sqlQueries
from feeds.rating import FeedRatingResetManager, ObjectResetOperationClassifier


class FeedDataManager(ABC):
    """Represents a feed in the system.
    An half-abstract class for all feed types.
    """

    def __init__(self, feed_id: int) -> None:
        self._id = feed_id
        self._url: str | None = None
        self._rating: FeedRatingResetManager | None = None

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
        if not self._is_valid_url(new_url):
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

    @staticmethod
    @abstractmethod
    def _is_valid_url(url: str) -> bool:
        """Abstract method to check if a url is valid
        depending on its type.
        """
        pass


class RSSFeedDataManager(FeedDataManager):
    """Concrete class for RSS feeds,
    with specific implementation for _is_valid_url function.
    """
    def __new__(cls, feed_id: int) -> object:
        # Intended for instance.__class__.__name__ call.
        # To avoid print of 'DataManager' in string output.
        # Needed in user.collections.UserCollectionResetController.__iadd__ and __isub__ methods.
        cls.__name__ = "RSSFeed"
        return super().__new__(cls, feed_id, (), {})
    @staticmethod
    def _is_valid_url(url: str) -> bool:
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


class HTMLFeed(FeedDataManager):
    """Concrete class for HTML feeds,
    with specific implementation for _is_valid_url function.
    """

    def __new__(cls, feed_id: int) -> object:
        # Intended for instance.__class__.__name__ call.
        # To avoid print of 'DataManager' in string output.
        # Needed in user.collections.UserCollectionResetController.__iadd__ and __isub__ methods.
        cls.__name__ = "HTMLFeed"
        return super().__new__(cls, feed_id, (), {})

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """static method to check whether the given url is valid for HTML feeds or not.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the url is valid, False otherwise.
        """
        return

    # TODO implemenation


class FeedFactory:
    """Factory for creating a custom feed object by url parameter"""

    @staticmethod
    def create(url: str) -> FeedDataManager:
        pass
