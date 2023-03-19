from typing import Tuple

from mysql.connector import errors
from mysql.connector.connection import MySQLConnection

import config
from database_cursor import MySQLCursorCM

class UserDataManager:
    def __init__(self, user_id: str) -> None:
        self.id = user_id

    @property
    def favorites(self) -> Tuple[Feed, ...]:
        with MySQLCursorCM() as cursor:
            cursor.execute(f"""
                           SELECT {config.DATABASE_TABLES_NAMES.feeds_table}.{config.FEEDS_DATA_COLUMNS.links}
                           FROM {config.DATABASE_TABLES_NAMES.feeds_table}
                           INNER JOIN {config.DATABASE_TABLES_NAMES.subscriptions_table} 
                           ON {config.DATABASE_TABLES_NAMES.feeds_table}.{config.FEEDS_DATA_COLUMNS.id} = {config.DATABASE_TABLES_NAMES.subscriptions_table}.{config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}
                           INNER JOIN {config.DATABASE_TABLES_NAMES.users_table} 
                           ON {config.DATABASE_TABLES_NAMES.subscriptions_table}.{config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {config.DATABASE_TABLES_NAMES.users_table}.{config.USERS_DATA_COLUMNS.id}
                           WHERE {config.DATABASE_TABLES_NAMES.users_table}.{config.USERS_DATA_COLUMNS.id} = {self.id}
                           """)
            return tuple(Feed(link[0]) for link in cursor.fetch_all())
    
    @favorites.setter
    def add_favorites(self, *wargs: Tuple[Feed, ...]) -> None:
        with MySQLCursorCM() as cursor:
            new_subscriptions = [(feed.id, self.id) for feed in wargs]
            cursor.execute(f"""
                           INSERT INTO {config.DATABASE_TABLES_NAMES.subscriptions_table} ({config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}, {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id})
                           VALUES (%s, %s)
                           """, 
                           new_subscriptions)

    @favorites.deleter
    def delete_favorites(self, *wargs: Tuple[Feed, ...]) -> None:
        with MySQLCursorCM() as cursor:
            cursor.execute(f"""
                           DELETE FROM {config.DATABASE_TABLES_NAMES.subscriptions_table}
                           WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                           AND {config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id in [feed.id for feed in wargs]}
                           """)

    def is_subscriber_to(self, *wargs: Tuple[Feed, ...]) -> bool:
        with MySQLCursorCM() as cursor:
            cursor.execute(f"""
                           SELECT {config.DATABASE_TABLES_NAMES.subscriptions_table}.{config.SUBSCRIPTIONS_DATA_COLUMNS.feed_id}
                           FROM {config.DATABASE_TABLES_NAMES.subscriptions_table}
                           WHERE {config.SUBSCRIPTIONS_DATA_COLUMNS.user_id} = {self.id}
                           """)
            return all(
                (
                    feed.id
                    in [subscription[0] for subscription in cursor.fetch_all()]
                    for feed in wargs
                )
            )

    @property
    def destinations(self) -> Tuple[Destination, ...]:
        pass

    @destinations.setter
    def add_destinations(self, *wargs: Tuple[Destination, ...]) -> None:
        pass

    @destinations.deleter
    def delete_destinations(self, *wargs: Tuple[Destination, ...]) -> None:
        pass

    def is_registered_at_address(self, Tuple[Destination, ...]) -> bool:
        pass

    @property
    def username(self) -> str:
        pass

    @username.set
    def change_username(self, username: str) -> None:
        pass

    @property
    def password(self) -> str:
        pass

    @password.setter
    def change_password(self, password: str) -> None:
        pass

    @property
    def sending_time() -> datetime:
        pass
    @sending_time.setter
    def change_sending_time(time: datetime) -> None:
        pass
    
    def __del__(self) -> None:
        pass