# TODO docs

from __future__ import annotations
from typing import Tuple, Set

from common import ObjectResetOperationClassifier
from feeds.feed import FeedDataManager
from address import AddressDataManager


class UserCollectionResetController:
    """Controller for resets of user collections
    """
    def __init__(self, *collection: Tuple[FeedDataManager | AddressDataManager, ...]):
        self.collection_set: Set[FeedDataManager | AddressDataManager] = set(collection)
        self._last_operation: ObjectResetOperationClassifier | None= None

    def __repr__(self) -> str:
        return str(self.collection_set)

    @property
    def last_operation(self) -> ObjectResetOperationClassifier | None:
        """Property getter for last_operation info.
        Designed to protect against direct assignment.
        """
        return self._last_operation

    def __eq__(self, other: UserCollectionResetController) -> bool:
        return self.collection_set == other.collection_set

    def __iadd__(self, other: UserCollectionResetController):
        if any(item in self.collection_set for item in other.collection_set):
            raise ValueError(f"One or more {other.__class__.__name__} already exists")
        self.collection_set.update(other.collection_set)
        self._last_operation = ObjectResetOperationClassifier.ADDITION

    def __isub__(self, other: UserCollectionResetController):
        if any(item not in self.collection_set for item in other.collection_set):
            raise KeyError(f"One or more {other.__class__.__name__} does not exist!")
        for elem in other.collection_set:
            self.collection_set.remove(elem)
        self._last_operation = ObjectResetOperationClassifier.SUBTRACTION

    def __len__(self):
        return len(self.collection_set)
