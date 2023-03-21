"""
Context manager implementation to manage the securely data base connection,
With automatic closing of the connection once is not needed.   
"""

from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

import config


class MySQLCursorCM:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.__host: str = config.SQL_HOST
        self.__username: str = config.SQL_USERNAME
        self.__password: str = config.SQL_PASSWORD
        self.connection: MySQLConnection | None = None
        self.cursor: MySQLCursor | None = None

    def __enter__(self) -> MySQLConnection:
        try:
            self.connection = MySQLConnection(
                host=self.__host,
                user=self.__username,
                password=self.__password,
                autocommit=True,
            )
            self.cursor = self.connection.cursor()
        except Error as err:
            print(err)
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.connection.close()
        self.cursor.close()
