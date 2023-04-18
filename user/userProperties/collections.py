# TODO docs

from __future__ import annotations
from typing import Tuple, Set

from common import ObjectResetOperationClassifier
from feeds.feed import Feed


# TODO rename to good name like Manager, or something like that.
class FeedsResetManager:
    def __init__(self, *feeds: Tuple[Feed, ...]):
        self.feeds_set: Set[Feed] = set(feeds)
        self._last_operation: ObjectResetOperationClassifier | None= None

    def __repr__(self) -> str:
        return str(self.feeds_set)

    @property
    def last_operation(self) -> ObjectResetOperationClassifier | None:
        """Property getter for last_operation info.
        Designed to protect against direct assignment.
        """
        return self._last_operation

    def __eq__(self, other: FeedsResetManager) -> bool:
        return self.feeds_set == other.feeds_set

    def __iadd__(self, other: FeedsResetManager):
        if any(feed in self.feeds_set for feed in other.feed_set):
            raise ValueError("One or more feed/s already exists")
        self.feeds_set.update(other.feeds_set)
        self._last_operation = ObjectResetOperationClassifier.ADDITION

    def __isub__(self, other: FeedsResetManager):
        if any(feed not in self.feeds_set for feed in other.feeds):
            raise KeyError("One or more feeds does not exist!")
        for elem in other.feeds_set:
            self.feeds_set.remove(elem)
        self._last_operation = ObjectResetOperationClassifier.SUBTRACTION

    def __len__(self):
        return len(self.feeds_set)



class Addresses:
    pass