from user import User


class UserNotFound(Exception):
    """Exception for username not found"""


class UserAlreadyExists(Exception):
    """Exception for username already exists: Username is taken"""


class PasswordNotUpdated(Exception):
    """Exception for password not updated: Last modified more than a year ago"""
    def __init__(self, message: str, user: User) -> None:
        self.user = user
        self.message = message
