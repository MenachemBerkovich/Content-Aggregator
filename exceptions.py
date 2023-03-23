#TODO module documentation

from user import User


class InvalidUserName(Exception):
    """Exception for invalid user name: Less than 6 or more than 8 characters long,
    or it includes non-alphanumeric characters"""


class BadUserName(Exception):
    """Exception for bad user name: Easy to guess"""


class UserNotFound(Exception):
    """Exception for username not found in database"""


class UserNameAlreadyExists(Exception):
    """Exception for username already exists: Username is taken"""


class InvalidPassword(Exception):
    """Exception for invalid password: Less than 8 or more than 10 characters long,
    or does not contain any of the following: an uppercase letter, a lowercase letter,
    a special character from the following [!@#$%]"""


class PasswordNotUpdated(Exception):
    """Exception for password not updated: Last modified more than a year ago"""

    def __init__(self, message: str, user: User) -> None:
        self.user = user
        self.message = message


class IncorrectPassword(Exception):
    """Exception for cases where the password is valid, but does not match the user name"""
    