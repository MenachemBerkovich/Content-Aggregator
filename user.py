"""Implementation for the User interface in the Content Aggregator system.
"""

from typing import Tuple

from database_cursor import MySQLCursorCM

import config
from feed import Feed
from user_properties.address import Address, AddressFactory
from user_properties.username import UserName
from user_properties.password import Password
from user_properties.time import Time


class User:
    """Represents a user in the system"""

    def __init__(self, user_id: str) -> None:
        self.id = user_id

    def __repr__(self):
        return f"User(id={self.id})"

    def __str__(self):
        return f"""User object with id={self.id}
                and properties:
                feeds        = {self.feeds},
                username     = {self.username},
                password     = {self.password},
                sending_time = {self.sending_time},
                addresses    = {self.addresses},
                """

    @property
    def feeds(self) -> Tuple[Feed, ...]:
        """Feeds property getter.
        Gets all feeds where this user is subscribed to.
        
        Returns:
            Tuple[Feed, ...]: A tuple of Feed objects.
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
        """Feeds property getter.
        Resets the feed subscriptions of the user.
        
        Args:
            new_feeds (Tuple[Feed, ...]): The new feeds tuple for user subscription modifying. 
        """
        del self.feeds
        self.add_feeds(new_feeds)

    @feeds.deleter
    def feeds(self) -> None:
        """Feeds property deleter.
        Deletes all feeds from the subscriptions of the user.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.subscriptions_table} 
                WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                """
            )

    def add_feeds(self, *feeds: Tuple[Feed, ...]) -> None:
        """Subscribes the user to some new feeds.

        Args:
            feeds (Tuple[Feed, ...]): The feeds to subscribe to.
            
        Raises:
            ValueError: If One or more of new_feeds already exists.
        """
        if any(new_feed in self.feeds for new_feed in feeds):
            raise ValueError("One or more feed/s already exists")
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
        """Deletes some feeds from the user subscriptions.
        
        Args:
            feeds (Tuple[Feed, ...]) : A tuple of feeds to be deleted.
        """
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.subscriptions_table}
                WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                AND {config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id} IN ({','.join(str(feed.id) for feed in feeds)})
                """
            )

    def is_subscribed_to(self, *feeds: Tuple[Feed, ...]) -> bool:
        """Checks if user is subscribed to the given feeds.

        Args:
            feeds (Tuple[Feed, ...]): A tuple of feeds to check for subscriptions.
        
        Returns:
            bool: True if user is subscribed to all the given feeds, False otherwise.
        """
        return all(feed in self.feeds for feed in feeds)

    @property
    def addresses(self) -> Tuple[Address, ...]:
        """Address property getter.
        Gets the existing addresses for this user.
        
        Returns:
            Tuple[Address, ...]: A tuple of Address objects, where this user is connected.
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
        """Adds a new address for this user.
        
        Args:
            new_addresses (Tuple[Address, ...]): A tuple of Address objects to add to this user.
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
        """Deletes all addresses from the database.
        
        Args:
            addresses (Tuple[Address, ...]): A tuple of address objects that candidate to deletion.
        
        Raises:
            ValueError: If any of the addresses does not exist, 
                        or if we have only one address right now.
        """
        if len(self.addresses) == 1:
            raise ValueError("You must provide at least one address!")
        if any(address not in self.addresses for address in addresses):
            raise ValueError("One or more addresses does not exist!")
        with MySQLCursorCM() as cursor:
            for address in addresses:
                cursor.execute(
                    f"""
                    DELETE {AddressFactory.match_db_index(address.address)} FROM {config.DATABASE_TABLES_NAMES.users_table}
                    WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                    """
                )

    def is_registered_at(self, *addresses: Tuple[Address, ...]) -> bool:
        """Checks if this user is registered at a given addresses.

        Args:
            addresses (Tuple[Address, ...]): A tuple of address objects to check if the user is registered in.
        
        Returns:
            bool: True if the user is registered at the given addresses, False otherwise.
        """
        return all(address in self.addresses for address in addresses)

    @property
    def username(self) -> UserName:
        """UserName property getter.
        Gets the username of this user.
        
        Returns:
            UserName: UserName object of this user.
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

    @username.setter
    def username(self, new_username: UserName) -> None:
        """UserName property setter.
        Sets the UserName of this user.
        
        Args:
            new_username (UserName): the new UserName for this user.
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
        """Password property getter.
        Gets the password object of this user.
        
        Returns:
            Password: The password of this user.
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
    def password(self, new_password: Password) -> None:
        """Password property setter.
        Sets the password of this user.
        
        Args:
            new_password (Password): The new password for this user.
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
        """sending_time property getter.
        Gets the Time object of this user.
        
        Returns:
            Time: The Time object of this user (including it's sending time and sending schedule).
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
    def sending_time(self, time: Time) -> None:
        """sending_time property setter.
        Sets the Time object of this user.
        
        Args:
            Time: The time to send the messages to this user.
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
        """Deletes this user from the database /& system.
        """
        del self.feeds
        with MySQLCursorCM() as cursor:
            cursor.execute(
                f"""
                DELETE * FROM {config.DATABASE_TABLES_NAMES.users_table}
                WHERE {config.USERS_DATA_COLUMNS.id} = {self.id}
                """
            )
