"""System-specific exceptions
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from contentAggregator.user.userInterface import User


class InvalidUserName(Exception):
    """Exception for invalid user name: Less than 6 or more than 8 characters long,
    or it includes non-alphanumeric characters"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 10


class InvalidPassword(Exception):
    """Exception for invalid password: Less than 8 or more than 10 characters long,
    or does not contain any of the following: an uppercase letter, a lowercase letter,
    a special character from the following [!@#$%]"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 8


class BadUserName(Exception):
    """Exception for bad user name: Easy to guess"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 9


class UserNotFound(Exception):
    """Exception for username not found in database"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 7


class UserNameAlreadyExists(Exception):
    """Exception for username already exists: Username is taken"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 7


class PasswordNotUpdated(Exception):
    """Exception for password not updated: Last modified more than a year ago"""
    def __init__(self, message: str, user: User) -> None:
        super().__init__(message)
        self.user = user
        self.criticality: int = 6


class IncorrectPassword(Exception):
    """Exception for cases where the password is valid, but does not match the user name"""
    def __init__(self, message: str):
        super().__init__(message)
        self.criticality: int = 5
        