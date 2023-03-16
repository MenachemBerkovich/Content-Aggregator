"""
_summary_
"""

from mysql.connector import errors 
from mysql.connector.connection import MySQLConnection

import config


class DBManager:
    pass


class MySQLManager(DBManager):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.__host: str = config.SQL_HOST
        self.__username: str = config.SQL_USERNAME
        self.__password: str = config.SQL_PASSWORD
        self.connection: MySQLConnection | None = None

    def __enter__(self) -> MySQLConnection:
        try:
            self.connection = MySQLConnection(
                host=self.__host,
                user=self.__username,
                password=self.__password,
            )
#TODO exact match except 
        except:
#TODO handle it with my own custom errors.py file
            pass
        return self.connection

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.connection.close()
