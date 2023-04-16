"""Designed to allow following after reset operations in the rating of feed.
It necessary, in order to enable protecting on the Feed.rating attribute as a property,
and still allow operations like +=, and -= in a protected way (with updates to the database). 
"""


from __future__ import annotations
from enum import Enum
from functools import total_ordering


@total_ordering
class FeedRatingManager:
    """Manager of feed's rating setter and getter interface.
    """
    def __init__(self, rating: float | None):
        if not rating:
            rating = 0
        self.rating = rating
        self._last_operation: ObjectResetOperationClassifier | None = None

    def __repr__(self) -> str:
        return str(self.rating)

    @property
    def last_operation(self) -> ObjectResetOperationClassifier | None:
        """Property getter for last_operation info.
        Designed to protect against direct assignment.
        """
        return self._last_operation

    def __iadd__(self, rating: float) -> None:
        self.rating += rating
        self._last_operation = ObjectResetOperationClassifier.ADDITION

    def __isub__(self, rating: float) -> None:
        self.rating -= rating
        self._last_operation = ObjectResetOperationClassifier.SUBTRACTION

    def __eq__(self, rating: float) -> bool:
        return self.rating == rating

    def __gt__(self, rating: float) -> bool:
        return self.rating > rating

class ObjectResetOperationClassifier(Enum):
    """Enum class contains possible setter's object operations, like:
    +=, -=, etc.
    """
    ADDITION = 1
    SUBTRACTION = 2
    