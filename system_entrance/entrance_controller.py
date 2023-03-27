"""Users entrance control - Enables to initialize a user sessions,
by login method or signup method. Including username and password verification.
"""

from typing import Tuple, List

from validators import (
    PRELIMINARY_USERNAME_CHECKERS,
    check_username_existence,
    PASSWORD_CHECKERS,
    check_credentials_compatibility,
)
import config
from database_cursor import MySQLCursorCM
from user import User


def __set_critical(exceptions: Tuple[Exception, ...]) -> Exception:
    """Sets the most critical exception of the exceptions tuple.

    Args:
        exceptions (Tuple[Exception, ...]): A tuple of exceptions that are candidates to be raised.

    Returns:
        Exception: The most critical exception of the exceptions tuple.
                   Determined by the criticality attribute of the exception.
    """
    return max(exceptions, key=lambda exception: exception.criticality)


def __get_credentials_report(username: str, password: str) -> List[Exception | None]:
    """Creates a list of the credentials verifiers results on the given username and password.

    Args:
        username (str): The username to check.
        password (str): The password to check.

    Returns:
        List[Exception | None]: A list of the credentials verifiers results.
    """
    return [checker(username) for checker in PRELIMINARY_USERNAME_CHECKERS] + [
        checker(password) for checker in PASSWORD_CHECKERS
    ]


def save_new_user(username: str, password: str) -> str:
    """Saves a new user to the database.

    Args:
        username (str): The username to save for the new user.
        password (str): The password to save for the new user.

    Returns:
        str: The new user row id.
    """
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
    """Enters users to the system, subject to the username and password correctness.

    Args:
        username (str): Username of the incoming user.
        password (str): Password of the incoming user.

    Raises:
        __set_critical: Appropriate exception in case an error occurs
                        during the authentication process.

    Returns:
        User: If the user is successfully logged in, returns the User object.
    """
    validation_list = __get_credentials_report(username, password) + [
        check_username_existence(username, True)
    ]
    if not any(validation_list):
        match = check_credentials_compatibility(username, password)
    if any(validation_list + [match]):
        # TODO in case of PasswordNotUpdated error  -
        # in the big session manager do except statement for this,
        # and when handle it by "as err" -> return err.user
        # and prints the massage for replace it's password
        raise __set_critical(
            tuple(filter(lambda event: isinstance(event, Exception), validation_list))
        )
    return User(match)


def sign_up(username: str, password: str) -> User:
    """Registers a new user accounts, by the chosen username and password.

    Args:
        username (str): The new username to register.
        password (str): The new password to register for this new username.
    
    Raises:
        __set_critical: Appropriate exception in case an error occurs
                        during the registration process.

    Returns:
        User: A User instance for the new user.
    """
    validation_list = __get_credentials_report(username, password) + [
        check_username_existence(username, False)
    ]
    if any(validation_list):
        raise __set_critical(
            tuple(filter(lambda event: isinstance(event, Exception), validation_list))
        )
    return User(save_new_user(username, password))
