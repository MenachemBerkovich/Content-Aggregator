"""Automatic messaging support.
Should work ay anytime - as a server.
Independent of any other system events, like client server interaction.
"""
from __future__ import annotations
from typing import NamedTuple, Tuple, Callable
from enum import Enum
import time
import contextlib

import schedule

from contentAggregator.sqlManagement import sqlQueries
from contentAggregator.user.userInterface import User
from contentAggregator.user.userProperties.time import Timing

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
        # update all remaining users
        # TODO consider improve the complexity by updating the modified only.
        for user_id in self._users_table.keys():
            self._users_table[user_id] = User(user_id)
        #insert new users
        new_users_set = updated_users_set.difference(self._users_table.keys())
        for user_id in new_users_set:
            self._users_table[user_id] = User(user_id)   
        self._set_schedules()

    def _create_job(self, job_timing: Timing) -> schedule.Job:
        match job_timing:
            case Timing.DAILY:
                return self._scheduler.every().day
            case Timing.MONDAY:
                return self._scheduler.every().monday
            case Timing.TUESDAY:
                return self._scheduler.every().tuesday
            case Timing.WEDNESDAY:
                return self._scheduler.every().wednesday
            case Timing.THURSDAY:
                return self._scheduler.every().thursday
            case Timing.FRIDAY:
                return self._scheduler.every().friday
            case Timing.SATURDAY:
                raise ValueError("It is Shabes Kodesh!!!, What are you doing?!")
            case Timing.SUNDAY:
                return self._scheduler.every().sunday

    # def _get_delivery_method(self, user: User) -> Tuple[Callable, str]:
    #     return prepare_message([feed.download() for feed in user.feeds.collection])
    #     #TODO docs and implementation
    #     pass

    def _set_schedules(self) -> None:
        for user in self._users_table.values():
            with contextlib.suppress(ValueError):
                job = self._create_job(user.sending_time.sending_schedule)
            #TODO match timezone also.
            job.at(user.sending_time.sending_time.strftime("%H:%M"))
            for address in user.addresses.collection.values():
                job.do(address.send_message, *(feed.content for feed in user.feeds.collection))

    def run(self) -> None:
        self._set_schedules()
        while True:
            self._scheduler.run_pending()
            #TODO: check user_table_correctness here by scheduling.
            time.sleep(1)


# class UsersTableEvent(NamedTuple):
#     """Organizes information about events that may occur in the users table,
#     like user deletion, user creation, user properties modifications.
#     """
#     user_id: str
#     event: UserEvents


# class UserEvents(Enum):
#     """Defined identities for each event may occur for some user.
#     """
#     ADDED = 1
#     DELETED = 2
#     FEEDS_UPDATED = 3
#     ADDRESSES_UPDATED = 4
