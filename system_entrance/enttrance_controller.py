from typing import Tuple

from user import User
import validators


def set_critical(exceptions: Tuple[Exception, ...]):
    return 


def log_in(username: str, password: str) -> User:
    validation_list = [validator(username) for validator in validators.USERNAME_VALIDATORS] + [
        validator(password) for validator in validators.PASSWORD_VALIDATORS
    ]
    if all(validator.boolean_val for validator in validation_list):
        match = validators.is_match(username, password)
    if any(validator.event for validator in validation_list + [match]):
        raise set_critical((validator.event for validator in validation_list if validator.event))
    return User(match.event)

def sign_up(username: str, password: str) -> User:
    pass
