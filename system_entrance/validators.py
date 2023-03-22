""""""


from typing import Tuple, Callable
from collections import namedtuple

from user import User


Report = namedtuple("Report", ("boolean_val", "event"))


def is_valid_username(suername: str) -> Report[bool, Exception | None]:
    pass


def is_bad_username(username: str) -> Report[bool, Exception | None]:
    """by blacklist

    Args:
        username (str): _description_
    """
    pass


def is_exists_username(username: str) -> Report[bool, Exception | None]:
    pass


def is_valid_password(password: str) -> Report[bool, Exception | None]:
    pass


def is_match(username: str, password: str) -> Report[bool, Exception | str]:
    return


USERNAME_VALIDATORS: Tuple[Callable[[str], Report], ...] = (
    is_valid_username,
    is_bad_username,
    is_exists_username,
)

PASSWORD_VALIDATORS: Tuple[Callable[[str], Report], ...] = (is_valid_password,)

# def is_blacklist_password(password: str):
#     pass
