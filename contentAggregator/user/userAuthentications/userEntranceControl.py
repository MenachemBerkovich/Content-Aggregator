"""Users entrance control - Enables to initialize a user sessions,
by login method or signup method. Including username and password verification.
"""
from typing import List
from datetime import datetime

from contentAggregator.user.userInterface import User
from contentAggregator import config
from contentAggregator.sqlManagement import sqlQueries

from contentAggregator.user.userAuthentications import pwdHandler
from contentAggregator.user.userAuthentications.validators import (
    PRELIMINARY_USERNAME_CHECKERS,
    PASSWORD_CHECKERS,
    check_username_existence,
    check_credentials_compatibility,
)


def _get_credentials_validation_report(
    username: str, password: str
) -> List[Exception | None]:
    """Creates a list of the credentials validators results on the given username and password.

    Args:
        username (str): The username to check.
        password (str): The password to check.

    Returns:
        List[Exception | None]: A list of the credentials validators results.
    """
    return [checker(username) for checker in PRELIMINARY_USERNAME_CHECKERS] + [
        checker(password) for checker in PASSWORD_CHECKERS
    ]


def __get_credentials_compatibility_report(
    username: str, password: str, required_val: bool
) -> Exception | int:
    """Creates a list of the credentials verifiers results on the given username and password.
    It is generated using the sql queries.
    It is designed and should be called,
    only if all results of the _get_credentials_validation_report, are None.

    Args:
        username (str): The username to check.
        password (str): The password to check.
        required_val (bool): The required value for the existence username checking,
                             True [in login session] or False [in signup session].

    Returns:
        Exception | int: Exception if something occurred.
                         else int - The row id of the requested account.
    """
    username_existence_exc = check_username_existence(username, required_val)
    verify_compatibility_exc = (
        None
        if username_existence_exc
        else check_credentials_compatibility(username, password)
    )
    return username_existence_exc or verify_compatibility_exc


def save_new_user(username: str, password: str) -> int:
    """Saves a new user to the database.

    Args:
        username (str): The username to save for the new user.
        password (str): The password to save for the new user.

    Returns:
        int: The new user row id.
    """
    return sqlQueries.insert(
        table=config.DATABASE_TABLES_NAMES.users_table,
        cols=(
            config.USERS_DATA_COLUMNS.username,
            config.USERS_DATA_COLUMNS.password,
            config.USERS_DATA_COLUMNS.last_password_change_date,
        ),
        values=(username, pwdHandler.encrypt_password(password), datetime.now().date()),
    )


def log_in(username: str, password: str) -> User:
    """Enters users to the system, subject to the username and password correctness.

    Args:
        username (str): Username of the incoming user.
        password (str): Password of the incoming user.

    Raises:
        event: Appropriate exception in case an error occurs
               during the authentication process.

    Returns:
        User: If the user is successfully logged in, returns the User object.
    """
    validation_list = _get_credentials_validation_report(username, password)
    event = (
        max(
            tuple(
                filter(
                    lambda event: isinstance(event, Exception),
                    validation_list,
                )
            ),
            key=lambda event: event.criticality,
        )
        if any(validation_list)
        else __get_credentials_compatibility_report(username, password, True)
    )
    if isinstance(event, Exception):
        # TODO in case of PasswordNotUpdated error  -
        # in the big session manager do except statement for this,
        # and when handle it by "as err" -> return err.user
        # and prints the massage for replace it's password
        raise event
    return User(event)


def sign_up(username: str, password: str) -> User:
    """Registers a new user accounts, by the chosen username and password.

    Args:
        username (str): The new username to register.
        password (str): The new password to register for this new username.

    Raises:
        event: Appropriate exception in case an error occurs
                        during the registration process.

    Helper functions:
        save_new_user: Saves the username and password of the new account in the database.

    Returns:
        User: A User instance for the new user.
    """
    validation_list = _get_credentials_validation_report(username, password)
    event = (
        max(
            tuple(filter(lambda event: isinstance(event, Exception), validation_list)),
            key=lambda event: event.criticality,
        )
        if any(validation_list)
        else check_username_existence(username, False)
    )

    if event:
        raise event
    return User(save_new_user(username, password))
