"""A set of functions that used to verify usernames and passwords.
both in terms of meeting the system requirements, and in terms of matching the existing data.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, List, Callable


from bcrypt import checkpw

import config
from database_cursor import MySQLCursorCM
from user import User
import exceptions


# bad usernames [easy to guess] that are not allowed in the system.
USERNAMES_BLACKLIST: List[str] = [
    "access",
    "account",
    "accounts",
    "alerts",
    "assets",
    "avatar",
    "backup",
    "banner",
    "banners",
    "billing",
    "billings",
    "bookmark",
    "business",
    "calendar",
    "campaign",
    "captcha",
    "careers",
    "category",
    "change",
    "channel",
    "channels",
    "checkout",
    "client",
    "comment",
    "comments",
    "compare",
    "compose",
    "config",
    "connect",
    "contact",
    "contest",
    "cookies",
    "create",
    "customer",
    "delete",
    "discuss",
    "domain",
    "download",
    "downvote",
    "editor",
    "errors",
    "events",
    "example",
    "explore",
    "export",
    "family",
    "features",
    "feedback",
    "filter",
    "follow",
    "follower",
    "forgot",
    "forums",
    "friend",
    "friends",
    "groups",
    "guides",
    "header",
    "hosting",
    "htpasswd",
    "images",
    "import",
    "insert",
    "invite",
    "invites",
    "invoice",
    "isatap",
    "issues",
    "license",
    "logout",
    "master",
    "member",
    "members",
    "message",
    "messages",
    "metrics",
    "mobile",
    "modify",
    "network",
    "nobody",
    "noreply",
    "oauth2",
    "offers",
    "online",
    "openid",
    "orders",
    "overview",
    "partners",
    "passwd",
    "password",
    "payment",
    "payments",
    "photos",
    "plugins",
    "policies",
    "policy",
    "popular",
    "postfix",
    "premium",
    "previous",
    "pricing",
    "privacy",
    "private",
    "product",
    "profile",
    "profiles",
    "project",
    "projects",
    "public",
    "purchase",
    "redirect",
    "reduce",
    "refund",
    "refunds",
    "register",
    "remove",
    "replies",
    "report",
    "request",
    "response",
    "return",
    "returns",
    "review",
    "reviews",
    "rootuser",
    "script",
    "search",
    "secure",
    "security",
    "select",
    "services",
    "session",
    "sessions",
    "settings",
    "signin",
    "signup",
    "sitemap",
    "source",
    "ssladmin",
    "staging",
    "static",
    "status",
    "styles",
    "support",
    "survey",
    "sysadmin",
    "system",
    "tablet",
    "telnet",
    "themes",
    "topics",
    "training",
    "trending",
    "unfollow",
    "update",
    "upgrade",
    "usenet",
    "username",
    "verify",
    "webmail",
    "website",
    "widget",
    "widgets",
    "yourname",
]

# Regex pattern for checking the validity of an password.
PASSWORD_REGEX_SEARCH: str = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%]).+$"


def check_username_validation(username: str) -> exceptions.InvalidUserName | None:
    """Checks the username validation.
       A valid username should be 6-8 letters long, and contain only alpha-numeric characters.

    Args:
        username (str): Username to check.

    Returns:
        exceptions.InvalidUserName | None: Appropriate exception if the username is invalid, otherwise None.
    """
    is_valid_flag = username.isalnum() and 6 <= len(username) <= 8
    return (
        None
        if is_valid_flag
        else exceptions.InvalidUserName(
            "A username should be 6-8 letters long, and include only alpha-numeric characters"
        )
    )


def check_username_quality(username: str) -> exceptions.BadUserName | None:
    """Checks the username quality.
       Quality of an username, determined by the usernames blacklist.

    Args:
        username (str): A username to check against the usernames blacklist.

    Returns:
        exceptions.BadUserName | None: Appropriate exception if username is bad, otherwise None.
    """
    is_bad_flag = username in USERNAMES_BLACKLIST
    return (
        exceptions.BadUserName(
            "Be careful! The chosen username is a good candidate for guessing. choose another."
        )
        if is_bad_flag
        else None
    )


def check_username_existence(
    username: str, required_val: bool
) -> exceptions.UserNameAlreadyExists | exceptions.UserNotFound | None:
    """Checks if the given username exists in the database.
    and returns the appropriate exception if not found, or if username exists
    - accordance to the request type [login or signup].

    Args:
        username (str): The username to check.
        required_val(bool): If username should be exist for the current function call.
                            For example: in a login session, the username should exist,
                            which is not the case in a registration session.

    Returns:
       exceptions.UserNameAlreadyExists | exceptions.UserNotFound | None:
            UserNameAlreadyExists exception if username is already exists but it should'nt exist.
            UserNotFound in the opposite case.
            otherwise returns None.
    """
    with MySQLCursorCM() as cursor:
        cursor.execute(
            f"""
                       SELECT {config.USERS_DATA_COLUMNS.username}
                       FROM {config.DATABASE_TABLES_NAMES.users_table}
                       WHERE {config.USERS_DATA_COLUMNS.username} = %s
                       """,
            (username,),
        )
        results = cursor.fetchone()
    return (
        exceptions.UserNameAlreadyExists(
            "Sorry, this username is already taken. Please choose another name."
        )
        if results and not required_val
        else exceptions.UserNotFound("Username does not exist.")
        if not results and required_val
        else None
    )


def check_password_validation(password: str) -> exceptions.InvalidPassword | None:
    """Checks the password validation.
       valid password should be  8-10 letters long,
       and include at least one uppercase letter, one lowercase letter,
       and special character from the following [!@#$%]

    Args:
        password (str): Password to check.

    Returns:
         InvalidPassword | None: InvalidPassword exception if password is invalid,
                                 otherwise None.
    """
    is_valid_flag = (
        re.match(PASSWORD_REGEX_SEARCH, password) and 8 <= len(password) <= 10
    )
    return (
        None
        if is_valid_flag
        else exceptions.InvalidPassword(
            """A password should be 8-10 letters long, and include at least one uppercase letter, one lowercase letter,
    a special character from the following [!@#$%]"""
        )
    )


def has_been_a_year(last_password_change_date: str) -> bool:
    """Checks if the last_password_change_date was more than a year ago.

    Args:
        last_password_change_date (str): The date the last change was made.

    Returns:
        bool: True if a year has passed, False otherwise.
    """
    last_modified = datetime.strptime(last_password_change_date, "%Y-%m-%d").date()
    return datetime.now().date() - last_modified >= timedelta(days=365)


def check_credentials_compatibility(
    username: str, password: str
) -> exceptions.IncorrectPassword | exceptions.PasswordNotUpdated | int:
    """Checks if the entered password matches the given username, by database query.

    Args:
        username (str): The username of the requested account.
        password (str): The password to check against the username.

    Returns:
        IncorrectPassword | PasswordNotUpdated | int:
            IncorrectPassword if password does not match the username.
            PasswordNotUpdated if password match to the username, but it should be updated.
            otherwise int - the User id for this account.
    """
    with MySQLCursorCM() as cursor:
        cursor.execute(
            f"""
                       SELECT {config.USERS_DATA_COLUMNS.password},
                       {config.USERS_DATA_COLUMNS.last_password_change_date},
                       {config.USERS_DATA_COLUMNS.id}
                       FROM {config.DATABASE_TABLES_NAMES.users_table}
                       WHERE {config.USERS_DATA_COLUMNS.username} = '{username}'
                       """
        )
        result = cursor.fetchone()
        is_match_flag = checkpw(
            password.encode(config.PASSWORD_ENCODING_METHOD),
            result[0].encode(config.PASSWORD_ENCODING_METHOD),
        )
    return (
        exceptions.PasswordNotUpdated("A new password must be chosen", User(result[2]))
        if is_match_flag and has_been_a_year(result[1])
        else result[2]
        if is_match_flag
        else exceptions.IncorrectPassword("The password is incorrect. Try again."),
    )


# A tuple of a function objects used for username initial validation.
PRELIMINARY_USERNAME_CHECKERS: Tuple[Callable[[str, str], Exception]] = (
    check_username_validation,
    check_username_quality,
)

# A tuple of a function objects used for password initial validation.
PASSWORD_CHECKERS: Tuple[Callable[[str], Exception]] = (check_password_validation,)
