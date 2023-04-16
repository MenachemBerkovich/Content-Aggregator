"""classes for Feed objects of a different types.
"""

from abc import ABC, abstractmethod

from feeds.rating import FeedRatingManager, ObjectResetOperationClassifier


class Feed(ABC):
    """Represents a feed in the system.
    An half-abstract class for all feed types.
    """
    def __init__(self, feed_id: int) -> None:
        self._id = feed_id
        self._url: str | None = None
        self._rating: FeedRatingManager | None = None

    def __repr__(self):
        return f"Feed(id={self._id})"

    def __str__(self):
        return f"""Feed object with id={self.id}
                and properties:
                url        = {self.url},
                rating    = {self.rating},
                """

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
            self._url = None #TODO sql query.
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
        # TODO here: update url query

    @property
    def rating(self) -> float:
        """rating property getter.

        Returns:
            float: The rating of this feed.
        """
        if not self._rating:
            rating = ""# TODO sql query for int rating
            self._rating  = FeedRatingManager(rating)
        return self._rating.rating

    @rating.setter
    def rating(self, new_rating: float) -> None:
        """rating property setter.
        can be done with +=, -= or simple assignment (=).

        Args:
            new_rating (float): The new_rating for reset the rating by him. 
        """
        if self._rating.last_operation == ObjectResetOperationClassifier.ADDITION:
            ""
            #TODO sql query should adds thr new rating
        elif self._rating.last_operation == ObjectResetOperationClassifier.SUBTRACTION:
            ""
            #TODO sql query should subtract thr new rating
        else:
            self._rating.rating = new_rating

    @staticmethod
    @abstractmethod
    def _is_valid_url(url: str) -> bool:
        """Abstract method to check if a url is valid
        depending on its type.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the url is valid, False otherwise.
        """
        pass


class RSSFeed(Feed):
    """Concrete class for RSS feeds,
    with specific implementation for _is_valid_url function.
    """
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """static method to check whether the given url is valid for RSS feeds or not.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the url is valid, False otherwise.
        """
        return
        # TODO implemenation


class HTMLFeed(Feed):
    """Concrete class for HTML feeds,
    with specific implementation for _is_valid_url function.
    """
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
    """Factory for creating a custom feed object by url parameter
    """
    @staticmethod
    def create(url: str) -> Feed:
        pass
