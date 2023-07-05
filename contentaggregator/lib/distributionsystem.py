"""Automatic messaging support.
Should work ay anytime - as a server.
Independent of any other system events, like client server interaction.
"""
from __future__ import annotations
from typing import NamedTuple, Tuple, Callable, Iterable
from enum import Enum
import time
import contextlib

import schedule

from contentaggregator.lib.exceptions import TimingError
from contentaggregator.lib.sqlmanagement import databaseapi
from contentaggregator.lib.user.userinterface import User
from contentaggregator.lib.user.userproperties.time import Timing


class Messenger:
    """Sending messages to users - according to their preferences and settings."""

    def __init__(self) -> None:
        self._email_scheduler = schedule.Scheduler()
        self._whatsapp_scheduler = schedule.Scheduler()
        self._sms_scheduler = schedule.Scheduler()
        self._phone_scheduler = schedule.Scheduler()
        self._users_table = {}
        if users_set := databaseapi.get_users_set():
            self._users_table = {user_id: User(user_id) for user_id in users_set}

    def _clear_user_tasks(self, user_id: int) -> None:
        """Clear all tasks belonging to the given user, by it's id.

        Args:
            user_id (int): The user id.
        """
        for scheduler in [
            self._email_scheduler,
            self._whatsapp_scheduler,
            self._sms_scheduler,
            self._phone_scheduler,
        ]:
            with contextlib.suppress(Exception):
                scheduler.clear(tag=user_id)

    def _ensure_users_table_correctness(self) -> None:
        """Checks if any changes occurred in the database table.
        If it did happen, the method will update self._users_table,
        and reset schedules as necessary.
        """
        print("I calld to update self._users_table")
        updated_users_set = databaseapi.get_users_set()
        delete_users_set = set(self._users_table.keys()).difference(updated_users_set)
        # delete deleted users and cancel it's jobs.
        for user_id in delete_users_set:
            self._users_table.pop(user_id)
            self._clear_user_tasks(user_id)
        # update all remaining users in users table and cancel it's old jobs.
        # TODO consider improve the complexity by updating the modified only.
        for user_id in self._users_table.keys():
            self._users_table[user_id] = User(user_id)
            self._clear_user_tasks(user_id)
        # insert new users
        new_users_set = updated_users_set.difference(self._users_table.keys())
        for user_id in new_users_set:
            self._users_table[user_id] = User(user_id)
        print(
            "This is the updated",
            [user.sending_time.sending_time for user in self._users_table.values()],
        )
        self._set_schedules(set_updating_schedule=False)

    def _create_job(self, job_timing: Timing, address_key: str) -> schedule.Job:
        """Create a new schedule.Job object for specific self._..._scheduler
        with accordance timing.

        Args:
            job_timing (Timing): The timing of the sending, as determined by the user.
            address_key (str) : The type of the address: email, whatsapp, sms or phone.

        Raises:
            TimingError: If sending timed to saturday.

        Returns:
            schedule.Job: The scheduled Job registered in accordance self._..._scheduler.
        """

        match job_timing:
            case Timing.DAILY:
                return self.__dict__[f"_{address_key}_scheduler"].every().day
            case Timing.MONDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().monday
            case Timing.TUESDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().tuesday
            case Timing.WEDNESDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().wednesday
            case Timing.THURSDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().thursday
            case Timing.FRIDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().friday
            case Timing.SATURDAY:
                raise TimingError("It is Shabes Kodesh!!!, What are you doing?!")
            case Timing.SUNDAY:
                return self.__dict__[f"_{address_key}_scheduler"].every().sunday

    def _set_schedules(self, set_updating_schedule: bool = True) -> None:
        """Adds all sending tasks to the self._scheduler, each user as it's preferences.

        Args:
            set_updating_schedule (bool, optional): If updating schedules is needed,
            for example, by the self._ensure_users_table_correctness is not,
            because it's already scheduled once system started.
            Defaults to True.
        """
        for user in self._users_table.values():
            # try:
            #     job = self._create_job(user.sending_time.sending_schedule)
            # except (TimingError, AttributeError):
            #     continue
            # # TODO match timezone also.
            # job.at(user.sending_time.sending_time.strftime("%H:%M"))
            try:
                for address_key, address in user.addresses.collection.items():
                    job = self._create_job(
                        user.sending_time.sending_schedule, address_key
                    )
                    # TODO match timezone also.
                    job.at(user.sending_time.sending_time.strftime("%H:%M"))
                    job.do(address.send_message, *user.feeds.collection).tag(user.id)
            except (TimingError, AttributeError):
                continue
        if set_updating_schedule:
            for scheduler in [
                self._email_scheduler,
                self._whatsapp_scheduler,
                self._sms_scheduler,
                self._phone_scheduler,
            ]:
                scheduler.every(5).minutes.do(self._ensure_users_table_correctness)

    def run(self) -> None:
        """Defines the schedules, and runs them."""
        self._set_schedules()
        # print([i.job_func for i in self._scheduler.get_jobs()])
        while True:
            # print(self._scheduler.idle_seconds)
            self._email_scheduler.run_pending()
            self._whatsapp_scheduler.run_pending()
            self._sms_scheduler.run_pending()
            self._phone_scheduler.run_pending()
            print(
                "Jobs:",
                self._email_scheduler.get_jobs(),
                "\n",
                "+",
                self._phone_scheduler.run_pending(),
            )
            time.sleep(1)
