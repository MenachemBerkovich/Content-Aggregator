"""Implementation for the User interface in the Content Aggregator system.
"""


from datetime import datetime


from contentAggregator.sqlManagement import sqlQueries
from contentAggregator.feeds.feed import FeedFactory
from contentAggregator.common import ObjectResetOperationClassifier
from contentAggregator import config
from contentAggregator.user.userAuthentications import pwdHandler
from contentAggregator.user.userAuthentications.validators import (
    check_password_validation,
    PRELIMINARY_USERNAME_CHECKERS,
    check_username_existence,
)
from .userProperties.address import AddressFactory
from .userProperties.time import Time
from .userProperties.collections import UserCollectionResetController


class User:
    """Represents a user in the system"""

    def __init__(self, user_id: int) -> None:
        self._id: int = user_id
        self._feeds: UserCollectionResetController | None = None
        self._addresses: UserCollectionResetController | None = None
        self._username: str | None = None
        self._password: str | None = None
        self._sending_time: str | None = None

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

    @property
    def id(self) -> int:
        """Property getter for user id in the users table.

        Returns:
            int: The row id of this user.
        """
        return self._id

    @property
    def feeds(self) -> UserCollectionResetController | None:
        """Feeds property getter.
        Gets all feeds where this user is subscribed to.

        Returns:
            UserCollectionResetController | None: An object contains an set of user feeds,
            if it has any feed,
            None otherwise.
        """
        if not self._feeds:
            if db_response := sqlQueries.select(
                cols=config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id,
                table=config.DATABASE_TABLES_NAMES.subscriptions_table,
                condition_expr=f"{config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self._id}",
            ):
                data = (FeedFactory.create(feed[0]) for feed in db_response)
                self._feeds = UserCollectionResetController(*data)
        return self._feeds

    @feeds.setter
    def feeds(self, feeds: UserCollectionResetController) -> None:
        """Feeds property setter.
        Resets the feed subscriptions of the user.

        Args:
            feeds (UserCollectionResetController): An object contains an set of user feeds
            to reset by them.
        """
        if self._feeds.last_operation == ObjectResetOperationClassifier.ADDITION:
            self._add_feeds(feeds)
        elif self._feeds.last_operation == ObjectResetOperationClassifier.SUBTRACTION:
            self._delete_feeds(feeds)
        else:
            self._delete_feeds(self.feeds)
            self._add_feeds(feeds)
            self._feeds = feeds

    def _add_feeds(self, feeds: UserCollectionResetController) -> None:
        """Subscribes the user to some new feeds.

        Args:
            feeds (UserCollectionResetController): The feeds to subscribe to.
        """
        sqlQueries.insert(
            table=config.DATABASE_TABLES_NAMES.subscriptions_table,
            cols=(
                config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id,
                config.SUBSCRIPTIONS_DATA_COLUMNS.user_id,
            ),
            values=([feed.id, self.id] for feed in feeds),
        )

    def _delete_feeds(self, feeds: UserCollectionResetController) -> None:
        """Deletes feeds from the user subscriptions.

        Args:
            feeds (UserCollectionResetController): An object contains an set of user feeds
            to be deleted.
        """
        sqlQueries.delete(
            table=config.DATABASE_TABLES_NAMES.subscriptions_table,
            condition_expr=f"""{config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self._id}
                            AND {config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}
                            IN ({','.join(str(feed.id) for feed in feeds.feeds_set)})""",
        )

    def is_subscribed_to(self, feeds: UserCollectionResetController) -> bool:
        """Checks if user is subscribed to the given feeds.

        Args:
            feeds (UserCollectionResetController): An object contains an set of user feeds
            to be deleted.

        Returns:
            bool: True if user is subscribed to all the given feeds, False otherwise.
        """
        return self.feeds == feeds

    # TODO continue embedding INTERFACE method like above (in feeds), and implement custom class
    # for this in collections.py module. consider to implement
    # an abstract class for UserCollectionResetController and AddressesResetManager
    # Implement __hash__ and __eq__ methods for Address class (so you can hold it in set of unique objects)
    # TODO Implement methods to enable using 'in' keyword, and to be iterable - UserCollectionResetController and AddressesResetManager classes
    @property
    def addresses(self) -> UserCollectionResetController | None:
        """Address property getter.
        Gets the existing addresses for this user.

        Returns:
            UserCollectionResetController | None: An object contains an set of user addresses,
            if he has any address.
            None otherwise.
        """
        if not self._addresses:
            desired_cols = (
                config.USERS_DATA_COLUMNS.phone_number,
                config.USERS_DATA_COLUMNS.whatsapp_number,
                config.USERS_DATA_COLUMNS.email,
            )
            if any(
                db_response := sqlQueries.select(
                    cols=desired_cols,
                    table=config.DATABASE_TABLES_NAMES.users_table,
                    condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                )[0]
            ):
                response_info = zip(desired_cols, (col[0] for col in db_response))
                data = tuple(
                    AddressFactory.create(address[0], address[1])
                    for address in response_info
                    if address[1]
                )
                self._addresses = UserCollectionResetController(*data)
        return self._addresses

    @addresses.setter
    def addresses(self, addresses: UserCollectionResetController) -> None:
        """Addresses property setter.
        Resets the addresses of the user, where he subscribed.

        Args:
            addresses (UserCollectionResetController): An object contains an set of user addresses
            to reset by them.
        """
        if self._addresses.last_operation == ObjectResetOperationClassifier.ADDITION:
            self._add_addresses(addresses)
        elif (
            self._addresses.last_operation == ObjectResetOperationClassifier.SUBTRACTION
        ):
            self._delete_addresses(addresses)
        else:
            self._delete_addresses(self.addresses)
            self._add_addresses(addresses)
            self._addresses = addresses

    def _add_addresses(self, new_addresses: UserCollectionResetController) -> None:
        """Adds a new address into this user.

        Args:
            new_addresses (UserCollectionResetController): An object contains an set of user addresses.
        """
        if new_addresses:
        # TODO maybe there is any method improve it by avoiding for loop?
            for address in new_addresses.collection_set:
                sqlQueries.update(
                    table=config.DATABASE_TABLES_NAMES.users_table,
                    updates_dict={address.db_index: address.address},
                    condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
                )

    def _delete_addresses(self, addresses: UserCollectionResetController) -> None:
        """Deletes all addresses from the database.

        Args:
            addresses (UserCollectionResetController): An object contains an
            set of user addresses to be deleted.
        """
        if addresses:
            sqlQueries.update(
                table=config.DATABASE_TABLES_NAMES.users_table,
                updates_dict={address.db_index: None for address in addresses},
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
            )

    def is_registered_at(self, addresses: UserCollectionResetController) -> bool:
        """Checks if this user is registered at a given addresses.

        Args:
            addresses (UserCollectionResetController): An object contains an set of user
        Returns:
            bool: True if the user is registered at the given addresses, False otherwise.
        """
        return addresses == self._addresses if self._addresses else False

    @property
    def username(self) -> str:
        """Username property getter.
        Gets the username of this user.

        Returns:
            str: The name of this user.
        """
        if not self._username:
            self._username = sqlQueries.select(
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
        sqlQueries.update(
            table=new_username,
            updates_dict={config.USERS_DATA_COLUMNS.username: new_username},
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
        )
        self._username = new_username

    @property
    def password(self) -> str:
        """Password property getter.
        Gets the password object of this user.

        Returns:
            str: The hashed password of this user.
        """
        if not self._password:
            self._password = sqlQueries.select(
                cols=config.USERS_DATA_COLUMNS.password,
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0][0]
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
        hashed_pwd = pwdHandler.encrypt_password(new_password)
        sqlQueries.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                config.USERS_DATA_COLUMNS.username: new_password,
                config.USERS_DATA_COLUMNS.password: hashed_pwd,
                config.USERS_DATA_COLUMNS.last_password_change_date: datetime.now().date(),
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
        self._password = new_password

    @property
    def sending_time(self) -> Time:
        """sending_time property getter.
        Gets the Time object of this user.

        Returns:
            Time: The Time object of this user (including it's sending time and sending schedule).
        """
        if not self._sending_time:
            db_response = sqlQueries.select(
                cols=(
                    config.USERS_DATA_COLUMNS.sending_time,
                    config.USERS_DATA_COLUMNS.sending_schedule,
                ),
                table=config.DATABASE_TABLES_NAMES.users_table,
                condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self._id}",
                desired_rows_num=1,
            )[0]
            if all(db_response):
                self._sending_time = Time(*db_response)
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
        sqlQueries.update(
            table=config.DATABASE_TABLES_NAMES.users_table,
            updates_dict={
                config.USERS_DATA_COLUMNS.sending_time: time.sending_time,
                config.USERS_DATA_COLUMNS.sending_schedule: time.sending_schedule,
            },
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
        self._sending_time = time

    def delete(self) -> None:
        """Deletes this user from the database."""
        if self.feeds:
            self._delete_feeds(self.feeds)
        sqlQueries.delete(
            table=config.DATABASE_TABLES_NAMES.users_table,
            condition_expr=f"{config.USERS_DATA_COLUMNS.id} = {self.id}",
        )
