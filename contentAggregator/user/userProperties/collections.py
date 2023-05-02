"""Intended to be used in cases of user collection resets,
it enables to control those operations.
For example: user.feeds += feeds_object - where type(feeds_object) is UserSetController.
By theses classes we can control and recognize
which operations we need to do in the database by the User interface.
"""

from __future__ import annotations
from typing import Tuple, Set, Dict
from abc import ABC, abstractmethod

from contentAggregator.common import ObjectResetOperationClassifier
from contentAggregator.feeds.feed import Feed
from contentAggregator.user.userProperties.address import Address


class UserCollectionResetController(ABC):
    """A semi-abstract class for controlling resets of user collections"""

    def __init__(
        self,
        *collection_set: Feed,
        **collection_dict: Address,
    ):
        """Creates a new reset controller for the given collection,
        by the template function '_create_collection',
        which implemented by inheritors.
        If Feeds objects are passed as positional arguments, then a set of them
        will be created,
        If Addresses objects are passed as keyword arguments, then a dict of them will be created."""
        self.collection: Set[Feed] | Dict[
            str, Address
        ] = self._create_collection(collection_set or collection_dict)
        self._last_operation: ObjectResetOperationClassifier | None = None

    def __repr__(self) -> str:
        return str(self.collection)

    @abstractmethod
    def _create_collection(
        self, collection: Tuple[Feed] | Dict[str, Address]
    ) -> Set[Feed] | Dict[str, Address]:
        """Template for creating a collection from the inheritors classes
        accordance to the case.

        Args:
            collection (Tuple[Feed] | Dict[str, Address]):
                The collection to be created.

        Returns:
            Set[Feed] | Dict[str, Address]: The collection as required type.
        """
        pass

    @property
    def last_operation(self) -> ObjectResetOperationClassifier | None:
        """Property getter for last_operation info.
        Designed to protect against direct assignment.
        """
        return self._last_operation

    def __eq__(self, other: UserCollectionResetController) -> bool:
        return self.collection == other.collection

    def __iadd__(self, other: UserCollectionResetController):
        if any(item in self.collection for item in other.collection):
            raise ValueError("One or more of this collection already exists")
        self.collection.update(other.collection)
        self._last_operation = ObjectResetOperationClassifier.ADDITION

    def __isub__(self, other: UserCollectionResetController):
        if any(item not in self.collection for item in other.collection):
            raise KeyError("One or more of this collection does not exist!")
        self._last_operation = ObjectResetOperationClassifier.SUBTRACTION

    def __len__(self):
        return len(self.collection)


class UserSetController(UserCollectionResetController):
    """Concrete class for mange user collections represented as a sets,
    like feeds of user.
    """

    def _create_collection(
        self, collection: Tuple[Feed]
    ) -> Set[Feed]:
        return set(collection)

    def __isub__(self, other: UserSetController):
        super().__isub__(self)
        for elem in other.collection:
            self.collection.remove(elem)
            


class UserDictController(UserCollectionResetController):
    """Concrete class for mange user collections represented as a dicts,
    like addresses of user. Maybe can passed to the __init__ as a form of ("email" = XXXX@Xxx.XX).
    """
    def _create_collection(
        self, collection: Dict[str, Address]
    ) -> Dict[Address, Address]:
        return collection

    def __isub__(self, other: UserDictController):
        super().__isub__(other)
        for key in other.collection.keys():
            self.collection.pop(key)
