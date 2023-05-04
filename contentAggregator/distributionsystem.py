"""Automatic messaging support.
Should work ay anytime - as a server.
Independent of any other system events, like client server interaction.
"""
from __future__ import annotations
import schedule
from typing import NamedTuple
from enum import Enum

from contentAggregator.sqlManagement import sqlQueries
from contentAggregator.user.userInterface import User 

class Messenger:
    """Sending messages to users - according to their preferences and settings.
    """

    def __init__(self) -> None:
        self._scheduler = schedule.Scheduler()
        self._users_table = {}
        if users_set := sqlQueries.get_users_set():
            self._users_table = {user_id: User(user_id) for user_id in users_set}

    def _check_users_table_correctness(self) -> None:
        updated_users_set = sqlQueries.get_users_set()
        delete_users_set = set(self._users_table.keys()).difference(updated_users_set)
        # delete deleted users
        for user_id in delete_users_set:
            self._users_table.pop(user_id)
        # update all users
        # TODO consider improve the complexity by updating the modified only.
        for user_id in self._users_table.keys():
            self._users_table[user_id] = User(user_id)
        #insert new users
        new_users_set = updated_users_set.difference(self._users_table.keys())
        for user_id in new_users_set:
            self._users_table[user_id] = User(user_id)

class UsersTableEvent(NamedTuple):
    """Organizes information about events that may occur in the users table,
    like user deletion, user creation, user properties modifications.
    """
    user_id: str
    event: UserEvents


class UserEvents(Enum):
    """Defined identities for each event may occur for some user.
    """
    ADDED = 1
    DELETED = 2
    FEEDS_UPDATED = 3
    ADDRESSES_UPDATED = 4
