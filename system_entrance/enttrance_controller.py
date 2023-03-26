# TODO documentation

from typing import Tuple, List

from validators import USERNAME_CHECKERS, PASSWORD_CHECKERS, is_match
import config
from database_cursor import MySQLCursorCM
from user import User


def __set_critical(exceptions: Tuple[Exception, ...]) -> Exception:
    return max(exceptions, key=lambda exception: exception.criticality)


def __get_credentials_report(username: str, password: str) -> List[Exception | None]:
    return [checker(username) for checker in USERNAME_CHECKERS] + [
        checker(password) for checker in PASSWORD_CHECKERS
    ]


def save_new_user(username: str, password: str) -> str:
    with MySQLCursorCM() as cursor:
        cursor.execute(
            f"""
                       INSERT INTO {config.DATABASE_TABLES_NAMES.users_table}
                       ({config.USERS_DATA_COLUMNS.username}, {config.USERS_DATA_COLUMNS.password})
                       VALUES (%s, %s)
                       """,
            (username, password),
        )
        return cursor.lastrowid()


def log_in(username: str, password: str) -> User:
    validation_list = __get_credentials_report(username, password)
    if not any(validation_list):
        match = is_match(username, password)
    if any(validation_list + [match]):
        #TODO in case of PasswordNotUpdated error  -
        # in the big session manager do except statement for this,
        # and when handle it by "as err" -> return err.user
        # and prints the massage for replace it's password
        raise __set_critical(tuple(filter(lambda event: isinstance(event, Exception), validation_list)))
    return User(match)


def sign_up(username: str, password: str) -> User:
    validation_list = __get_credentials_report(username, password)
    if any(validation_list):
        raise __set_critical(tuple(filter(lambda event: isinstance(event, Exception), validation_list)))
    return User(save_new_user(username, password))
