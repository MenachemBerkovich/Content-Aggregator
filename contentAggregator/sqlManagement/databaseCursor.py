"""
Context manager implementation to manage securely data base connection,
With automatic closing of the connection once is not needed.   
"""

from mysql.connector.errors import Error, InternalError
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from contentAggregator import config


class MySQLCursorCM:
    """Context manager for easy MySQL connection.
    """
    def __init__(self):
        self.__host: str = config.SQL_HOST
        self.__username: str = config.SQL_USERNAME
        self.__password: str = config.SQL_PASSWORD
        self.__database: str = config.DATABASE_NAME
        self.connection: MySQLConnection | None = None
        self.cursor: MySQLCursor | None = None

    def __enter__(self) -> MySQLConnection:
        try:
            self.connection = MySQLConnection(
                host=self.__host,
                user=self.__username,
                password=self.__password,
                database=self.__database,
                autocommit=True,
            )
            self.cursor = self.connection.cursor()
        except Error as err:
            print(err)
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        try:
            self.cursor.close()
            self.connection.close()
        except InternalError:
            self.cursor.fetchall()
            self.connection.close()
            self.cursor.close()
