"""Implementation for the User interface in the Content Aggregator system.
"""

from __future__ import annotations
import datetime
import json
import contextlib

from contentaggregator.lib.sqlmanagement import databaseapi
from contentaggregator.lib.feeds.feed import FeedFactory
from contentaggregator.lib import config
from contentaggregator.lib.user.userauthentications import pwdhandler
from contentaggregator.lib.user.userauthentications.validators import (
    check_password_validation,
    PRELIMINARY_USERNAME_CHECKERS,
    check_username_existence,
)
from contentaggregator.lib.user.userproperties import address
from contentaggregator.lib.user.userproperties.time import Time, Timing
from contentaggregator.lib.user.userproperties.collections import (
    UserDictController,
    UserSetController,
)
from contentaggregator.lib.exceptions import UserNotFound


class User:
    """Represents a user in the system"""

    def __init__(self, user_id: int) -> None:
        if not self.is_valid_id(user_id):
            raise UserNotFound("The user id is not valid.")
        self._id: int = user_id
        self._feeds: UserSetController | None = None
        self._addresses: UserDictController | None = None
        self._username: str | None = None
        self._password: bytes | None = None
        self._sending_time: Time | None = None

    def __repr__(self):
        return f"User(id={self.id})"

    def __str__(self):
        return f"""User object with id={self._id}
                and properties:
                feeds        = {self.feeds},
                username     = {self.username},
                password     = {self.password},
                sending_time = {self.sending_time},
                addresses    = {self.addresses},
                """

    def __eq__(self, other: User) -> bool:
        return (
            self._id == other._id
            and self.username == other.username
            and self.password == other.password
            and self.feeds == other.feeds
            and self.addresses == other.addresses
            and self.sending_time == other.sending_time
        )

    @staticmethod
    def is_valid_id(user_id: int) -> bool:
        """Checks if the given user id is valid i.e if it's exist in database.

        Args:
            user_id (int): The user id to check.

        Returns:
            bool: True if the user id exists in users table, False otherwise.
        """
        users_list = databaseapi.get_users_set()
        return user_id in users_list if users_list else False

    @property
    def id(self) -> int:
        """Property getter for user id in the users table.

        Returns:
            int: The row id of this user.
        """
        return self._id

    @property
    def feeds(self) -> UserSetController | None:
        """Feeds property getter.
        Gets all feeds where this user is subscribed to.

        Returns:
            UserSetController | None: An object contains an set of user feeds,
            if it has any feed,
            None otherwise.
        """
        if not self._feeds:
            if db_response := databaseapi.select(
                cols=config.USERS_DATA_COLUMNS.subscriptions,
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0][0]:
                # TODO for feed factory, we need send also the type of the feed. maybe by join query above,
                # that will be collect information from feeds table also. (or if it will be better to know this by url it self)
                data = (FeedFactory.create(feed) for feed in json.loads(db_response))
                self._feeds = UserSetController(*data)
        return self._feeds

    @feeds.setter
    def feeds(self, feeds: UserSetController) -> None:
        """Feeds property setter.
        Resets the feed subscriptions of the user.

        Args:
            feeds (UserSetController): An object contains an set of user feeds
            to reset by them.
        """
        if not self._feeds or not self._feeds.last_operation:
            self._feeds = feeds
        self._update_feeds()

    def _update_feeds(self) -> None:
        """Updates the user subscriptions as required by feeds.setter (+=, -= or assignment)."""
        databaseapi.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                config.USERS_DATA_COLUMNS.subscriptions: repr(
                    json.dumps([feed.id for feed in self._feeds.collection])
                )
                if self._feeds
                else None
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )

    def is_subscribed_to(self, feeds: UserSetController) -> bool:
        """Checks if user is subscribed to the given feeds.

        Args:
            feeds (UserSetController): An object contains an set of user feeds
            to be deleted.

        Returns:
            bool: True if user is subscribed to all given feeds, False otherwise.
        """
        return self.feeds == feeds

    # TODO Implement methods to enable using 'in' keyword, and to be iterable - UserCollectionResetController and AddressesResetManager classes
    @property
    def addresses(self) -> UserDictController | None:
        """Address property getter.
        Gets the existing addresses for this user.

        Returns:
            UserDictController | None: An object contains an set of user addresses,
            if he has any address.
            None otherwise.
        """
        if not self._addresses:
            if db_response := databaseapi.select(
                cols=config.USERS_DATA_COLUMNS.addresses,
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0][0]:
                response_info = json.loads(db_response)
                print(response_info)
                data = {
                    key: address.AddressFactory.create(key, value)
                    for key, value in response_info.items()
                }
                self._addresses = UserDictController(**data)
        return self._addresses

    @addresses.setter
    def addresses(self, addresses: UserDictController) -> None:
        """Addresses property setter.
        Resets the addresses of the user, where he subscribed.

        Args:
            addresses (UserDictController): An object contains an dict of user addresses
            to reset by them.
        """
        if not self._addresses or not self._addresses.last_operation:
            self._addresses = addresses
        self._update_addresses()

    def _update_addresses(self) -> None:
        """Updates the user subscriptions as required by feeds.setter (+=, -= or assignment)."""
        databaseapi.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                config.USERS_DATA_COLUMNS.addresses: repr(
                    json.dumps(
                        {
                            address_type: address.address
                            for address_type, address in self._addresses.collection.items()
                        }
                    )
                )
                if self._addresses
                else None
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )

    def is_registered_at(self, addresses: UserDictController) -> bool:
        """Checks if this user is registered at a given addresses.

        Args:
            addresses (UserDictController): An object contains an set of user addresses.
        Returns:
            bool: True if the user is registered at the given addresses, False otherwise.
        """
        return (
            all(
                item in self.addresses.collection.items()
                for item in addresses.collection.items()
            )
            if self.addresses
            else False
        )

    @property
    def username(self) -> str:
        """Username property getter.
        Gets the username of this user.

        Returns:
            str: The name of this user.
        """
        if not self._username:
            self._username = databaseapi.select(
                cols=config.USERS_DATA_COLUMNS.username,
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
                desired_rows_num=1,
            )[0][0]
        return self._username

    @username.setter
    def username(self, new_username: str) -> None:
        """username property setter.
        Sets the Username of this user.

        Args:
            new_username (str): the new username for this user.

        Raises:
            max: most critical error if is username invalid.
            username_existence_exc: if new_username already exists in another account.
        """
        report = [checker(new_username) for checker in PRELIMINARY_USERNAME_CHECKERS]
        if any(report):
            raise max(
                filter(lambda event: isinstance(event, Exception), report),
                key=lambda x: x.criticality,
            )
        if username_existence_exc := check_username_existence(new_username, False):
            raise username_existence_exc
        databaseapi.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={config.USERS_DATA_COLUMNS.username: repr(new_username)},
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
        )
        self._username = new_username

    @property
    def password(self) -> bytes:
        """Password property getter.
        Gets the password object of this user.

        Returns:
            bytes: The hashed password of this user.
        """
        if not self._password:
            self._password = bytes(
                databaseapi.select(
                    cols=config.USERS_DATA_COLUMNS.password,
                    table=config.DATABASE_TABLES_NAMES.users_table,
                    condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                    desired_rows_num=1,
                )[0][0]
            )
        return self._password

    @password.setter
    def password(self, new_password: str) -> None:
        """Password property setter.
        Sets the password of this user.

        Args:
            new_password (str): The new raw password for this user.

        Raises:
            event: if password is invalid
            by one or more conditions of the check_password_validation.
        """
        if event := check_password_validation(new_password):
            raise event
        hashed_pwd = pwdhandler.encrypt_password(new_password)
        databaseapi.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                # Using repr and decode to update sql with regular string like: '@weer8S!~~'
                # Unlike in sign_up method that uses insert query.
                config.USERS_DATA_COLUMNS.password: repr(
                    hashed_pwd.decode(config.PASSWORD_ENCODING_METHOD)
                ),
                # Using repr and str to update the date with str like: '2015-09-23'
                # Unlike in sign_up method that uses the insert query.
                config.USERS_DATA_COLUMNS.last_password_change_date: repr(
                    str(datetime.datetime.now().date())
                ),
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
        self._password = hashed_pwd

    @property
    def sending_time(self) -> Time:
        """sending_time property getter.
        Gets the Time object of this user.

        Returns:
            Time: The Time object of this user (including it's sending time and sending schedule).
        """
        if not self._sending_time:
            db_response = databaseapi.select(
                cols=(
                    config.USERS_DATA_COLUMNS.sending_time,
                    config.USERS_DATA_COLUMNS.sending_schedule,
                ),
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0]

            if all(db_response):
                self._sending_time = Time(
                    datetime.datetime.strptime(db_response[0], "%H:%M").time(),
                    Timing._value2member_map_[db_response[1]],
                )
            else:
                raise ValueError(
                    """Could not find any timing settings.
                    You must define sending preferences"""
                )
        return self._sending_time

    @sending_time.setter
    def sending_time(self, time: Time) -> None:
        """sending_time property setter.
        Sets the Time object of this user.

        Args:
            Time: The time to send the messages to this user.
        """
        databaseapi.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                config.USERS_DATA_COLUMNS.sending_time: time.sending_time.strftime(
                    "%H:%M"
                ),
                config.USERS_DATA_COLUMNS.sending_schedule: time.sending_schedule.value,
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
        self._sending_time = time

    def delete(self) -> None:
        """Deletes this user from the database."""
        databaseapi.delete(
            table=config.DATABASE_TABLES_NAMES.users_table,
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
