"""_summary_

Raises:
    ValueError: _description_
    ValueError: _description_

Returns:
    _type_: _description_
"""


from typing import Tuple

from database_cursor import MySQLCursorCM

import config
from feed import Feed
from user_properties.address import Address, AddressFactory
from user_properties.username import UserName
from user_properties.password import Password
from user_properties.time import Time 


class UserDataManager:
    def __init__(self, user_id: str) -> None:
        self.id = user_id

    @property
    def feeds(self) -> Tuple[Feed, ...]:
        """
        to get all Feed objects of the user.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                SELECT {config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}
                FROM {config.DATABASE_TABLES_NAMES.subscriptions_table}
                WHERE {config.DATABASE_TABLES_NAMES.subscriptions_table}.{config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                """
            )
            return tuple(Feed(feed[0]) for feed in cursor.fetch_all())

    @feeds.setter
    def feeds(self, *new_feeds: Tuple[Feed, ...]) -> None:
        """for reset all feeds of the user

        Raises:
            ValueError: _description_
        """
        if any(new_feed in self.feeds for new_feed in new_feeds):
            raise ValueError("One or more feed/s already exists")
        del self.feeds
        self.add_feeds(new_feeds)

    @feeds.deleter
    def feeds(self) -> None:
        """
        to delete all feeds of the user 
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.subscriptions_table} 
                WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                """
            )

    def add_feeds(self, *feeds: Tuple[Feed, ...]) -> None:
        """
        for subscribe to new and additional feeds 
        """
        with MySQLCursorCM() as cursor:
            new_subscriptions = [(feed.id, self.id) for feed in feeds]
            cursor.execute(
                f"""
                INSERT INTO {config.DATABASE_TABLES_NAMES.subscriptions_table}
                            ({config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}, {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id})
                VALUES (%s, %s)
                """,
                new_subscriptions,
            )

    def delete_feeds(self, *feeds: Tuple[Feed, ...]) -> None:
        """
        to delete some feeds from the user feeds
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.subscriptions_table}
                WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                AND {config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id} IN ({','.join(str(feed.id) for feed in feeds)})
                """
            )

    def is_subscriber_to(self, *feeds: Tuple[Feed, ...]) -> bool:
        """check if user is subscriber to the given feeds

        Returns:
            bool: _description_
        """
        return all(feed in self.feeds for feed in feeds)

    @property
    def addresses(self) -> Tuple[Address, ...]:
        """to get all existing addresses of the user
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                SELECT {config.USERS_DATA_COLUMNS.phone_number}, {config.USERS_DATA_COLUMNS.email} 
                FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.DATABASE_TABLES_NAMES.users_table}.{config.USERS_DATA_COLUMNS.id}
                        = {self.id}
                """
            )
            return tuple(
                AddressFactory.create(address) for address in cursor.fetch_one()
            )

    def add_addresses(self, *new_addresses: Tuple[Address, ...]) -> None:
        """
        to add one ore more addresses to the user
        """
        with MySQLCursorCM() as cursor:
            for address in new_addresses:
                cursor.execute(
                    f"""
                    INSERT INTO {config.DATABASE_TABLES_NAMES.subscriptions_table} ({AddressFactory.match_db_index(address)})
                    VALUES ({address})
                    """
                )

    def delete_addresses(self, *addresses: Tuple[Address, ...]) -> None:
        """for delete some addresses from the adrreses of the user
        """
        if len(self.addresses) == 1:
            raise ValueError("You must provide at least one address!")
        with MySQLCursorCM() as cursor:
            for address in addresses:
                cursor.execute(
                    f"""
                    DELETE {AddressFactory.match_db_index(address.address)} FROM {config.DATABASE_TABLES_NAMES.users_table}
                    WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                    """
                )

    def is_registered_at(self, *addresses: Tuple[Address, ...]) -> bool:
        """if this user registered at the given address.

        Returns:
            bool: _description_
        """
        return all(address in self.addresses for address in addresses)

    @property
    def username(self) -> UserName:
        """property for getting the username.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                SELECT {config.USERS_DATA_COLUMNS.username}
                FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )
            return UserName(cursor.fetch_one()[0])

    @username.set
    def change_username(self, new_username: UserName) -> None:
        """
        property for set or reset username.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                UPDATE {config.DATABASE_TABLES_NAMES.users_table}
                SET {config.USERS_DATA_COLUMNS.username} = {new_username.username}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )

    @property
    def password(self) -> Password:
        """
        password property to get the user's hashed password
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                SELECT {config.USERS_DATA_COLUMNS.password}
                FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )
            if not cursor.fetch_one():
                raise ValueError("Password does not exist yet")
            return Password(cursor.fetch_one()[0])

    @password.setter
    def change_password(self, new_password: Password) -> None:
        """
        for set or reset the password.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                UPDATE {config.DATABASE_TABLES_NAMES.users_table}
                SET {config.USERS_DATA_COLUMNS.username} = {new_password.password}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )

    @property
    def sending_time(self) -> Time:
        """
        property representing the timing of when messages sent to the addresses of user.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                SELECT {config.USERS_DATA_COLUMNS.sending_time}, {config.USERS_DATA_COLUMNS.sending_schedule}
                FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )
            return Time(cursor.fetch_one()[0], cursor.fetch_one()[1])

    @sending_time.setter
    def change_sending_time(self, time: Time) -> None:
        """
        for change the timing of the messages sending
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                UPDATE {config.DATABASE_TABLES_NAMES.users_table}
                SET {config.USERS_DATA_COLUMNS.sending_time} = {time.sending_time}, 
                    {config.USERS_DATA_COLUMNS.sending_schedule} = {time.sending_schedule}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )

    def __del__(self) -> None:
        """
        for delete the user from the database.
        """
        del self.feeds
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )
