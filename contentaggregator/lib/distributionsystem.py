"""Automatic messaging support.
Should work ay anytime - as a server.
Independent of any other system events, like client server interaction.
"""
from __future__ import annotations
from typing import NamedTuple, Tuple, Callable
from enum import Enum
import time

import schedule

from contentaggregator.lib.exceptions import TimingError
from contentaggregator.lib.sqlmanagement import databaseapi
from contentaggregator.lib.user.userinterface import User
from contentaggregator.lib.user.userproperties.time import Timing

class Messenger:
    """Sending messages to users - according to their preferences and settings.
    """

    def __init__(self) -> None:
        self._scheduler = schedule.Scheduler()
        self._users_table = {}
        if users_set := databaseapi.get_users_set():
            self._users_table = {user_id: User(user_id) for user_id in users_set}

    def _ensure_users_table_correctness(self) -> None:
        """Checks if any changes occurred in the database table.
        If it did happen, the method will update self._users_table,
        and reset schedules as necessary.
        """
        updated_users_set = databaseapi.get_users_set()
        delete_users_set = set(self._users_table.keys()).difference(updated_users_set)
        # delete deleted users and cancel it's jobs.
        for user_id in delete_users_set:
            self._users_table.pop(user_id)
            self._scheduler.clear(tag=user_id)
        # update all remaining users in users table and cancel it's old jobs.
        # TODO consider improve the complexity by updating the modified only.
        for user_id in self._users_table.keys():
            self._users_table[user_id] = User(user_id)
            self._scheduler.clear(tag=user_id)
        #insert new users
        new_users_set = updated_users_set.difference(self._users_table.keys())
        for user_id in new_users_set:
            self._users_table[user_id] = User(user_id)
        self._set_schedules()

    def _create_job(self, job_timing: Timing) -> schedule.Job:
        """Create a new schedule.Job object with accordance timing.

        Args:
            job_timing (Timing): The timing of the sending, as determined by the user.

        Raises:
            TimingError: If sending timed to saturday. 

        Returns:
            schedule.Job: The scheduled Job registered in self._scheduler.
        """
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
                raise TimingError("It is Shabes Kodesh!!!, What are you doing?!")
            case Timing.SUNDAY:
                return self._scheduler.every().sunday

    def _set_schedules(self) -> None:
        """Adds all sending tasks to the self._scheduler, each user as it's preferences.
        """
        for user in self._users_table.values():
            try:
                job = self._create_job(user.sending_time.sending_schedule)
            except (TimingError, AttributeError):
                continue
            #TODO match timezone also.
            job.at(user.sending_time.sending_time.strftime("%H:%M"))
            for address in user.addresses.collection.values():
                print(address)
                job.do(address.send_message, *user.feeds.collection).tag(user.id)
                print("job_finc", job.job_func)
                print(self._scheduler.get_jobs())
        self._scheduler.every(5).minutes.do(self._ensure_users_table_correctness)

    def run(self) -> None:
        """Defines the schedules, and runs them.
        """
        self._set_schedules()
        print([i.job_func for i in self._scheduler.get_jobs()])
        while True:
            print(self._scheduler.idle_seconds)
            self._scheduler.run_pending()
            time.sleep(1)
