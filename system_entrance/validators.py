# TODO documentation

""""""

import re
from datetime import datetime, timedelta
from typing import Tuple, List, Callable


from bcrypt import checkpw

import config
from database_cursor import MySQLCursorCM
from user import User
import exceptions


# TODO better type hint for variable number of strings in the list
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

# Regex pattern for checking the validity of a password
PASSWORD_REGEX_SEARCH: str = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%]).+$"


def check_username_validation(username: str) -> Exception | None:
    """

    Args:
        username (str): _description_

    Returns:
        Report[bool, Exception | None]: _description_
    """
    is_valid_flag = username.isalnum() and 6 <= len(username) <= 8
    return (
        exceptions.InvalidUserName(
            "A username should be 6-8 letters long, and include only alpha-numeric characters"
        )
        if is_valid_flag
        else None
    )


def check_username_quality(username: str) -> Exception | None:
    """_summary_

    Args:
        username (str): _description_

    Returns:
        Report[bool, Exception | None]: _description_
    """
    is_bad_flag = username in USERNAMES_BLACKLIST
    return (
        exceptions.BadUserName(
            "Be careful! The chosen username is a good candidate for guessing. choose another."
        )
        if is_bad_flag
        else None
    )


def check_username_existence(username: str, required_val: bool) -> Exception | None:
    """ """
    with MySQLCursorCM() as cursor:
        cursor.execute(
            f"""
                       SELECT {config.USERS_DATA_COLUMNS.username}
                       FROM {config.DATABASE_TABLES_NAMES.users_table}
                       WHERE {config.USERS_DATA_COLUMNS.username} = {username}
                       """
        )
        is_exist_flag = cursor.rowcount
    return (
        exceptions.UserNameAlreadyExists(
            "Sorry, this username is already taken. Please choose another name."
        )
        if is_exist_flag and not required_val
        else exceptions.UserNotFound("Username does not exist.")
        if not is_exist_flag and required_val
        else None
    )


def check_password_validation(password: str) -> Exception | None:
    """_summary_

    Args:
        password (str): _description_

    Returns:
        Report[bool, Exception | None]: _description_
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
    """_summary_

    Args:
        last_password_change_date (str): _description_

    Returns:
        bool: _description_
    """
    last_modified = datetime.strptime(last_password_change_date, "%Y-%m-%d %H:%M:%S")
    return datetime.now() - last_modified >= timedelta(days=365)


def is_match(username: str, password: str) -> Exception | str:
    """ """
    with MySQLCursorCM() as cursor:
        cursor.execute(
            f"""
                       SELECT {config.USERS_DATA_COLUMNS.password},
                       {config.USERS_DATA_COLUMNS.last_password_change_date},
                       {config.USERS_DATA_COLUMNS.id}
                       FROM {config.DATABASE_TABLES_NAMES.users_table}
                       WHERE {config.USERS_DATA_COLUMNS.username} = {username}
                       """
        )
        result = cursor.fetch_one()
        is_match_flag = checkpw(
            password.encode(config.PASSWORD_ENCODING_METHOD), result[0]
        )
    return (
        exceptions.PasswordNotUpdated("A new password must be chosen", User(result[2]))
        if is_match_flag and has_been_a_year(result[1])
        else result[2]
        if is_match_flag
        else exceptions.IncorrectPassword("The password is incorrect. Try again."),
    )


USERNAME_CHECKERS: Tuple[Callable[[str, str], Exception]] = (
    check_username_validation,
    check_username_quality,
    check_username_existence,
)

PASSWORD_CHECKERS: Tuple[Callable[[str], Exception]] = (check_password_validation,)
