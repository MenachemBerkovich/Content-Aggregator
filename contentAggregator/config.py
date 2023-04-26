"""This is the configuration file for allowing other users to define their own configuration
like data base credentials, database name, data tables name and columns of data tables.
"""
from dataclasses import dataclass
from typing import Dict


SQL_USERNAME: str | None = None

SQL_HOST: str | None = None

SQL_PASSWORD: str | None = None

DATABASE_NAME: str | None = None


@dataclass
class TablesNames:
    """
    The TablesNames for DATABASE_TABLES_NAMES modifying.
    contains the names of tables in the DATABASE_NAME environment.

    Object Attributes:
        users_table (str): User table information name.
        feeds_table (str): Link table information name.

    Examples:
        >>> my_tables = TablesNames()
        >>> my_tables.users_table
        None
        >>> my_tables.users_table = "users_info"
        >>> my_tables.feeds_table = "resources_info"
        >>> my_tables.users_table
        users_information
        >>> my_tables.feeds_table
        resources_links
    """

    users_table: str = "users_info"
    feeds_table: str = "feeds_info"
    subscriptions_table: str = "subscriptions_info"


DATABASE_TABLES_NAMES = TablesNames()


@dataclass
class UsersDataColumns:
    """
    The UsersDataColumns for USERS_DATA_COLUMNS modifying.
    contains the names of columns in the user data table.

    Object Attributes:
        id (str): Name of the id's column.
        username (str): Name of usernames column.
        password (str): Name of the password hash values column.

    Examples:
        >>> my_user_data_attributes = UsersDataColumns()
        >>> my_tables.id
        id
        >>> my_user_data_attributes.id = "id_columns"
        >>> my_user_data_attributes.id
        id_columns
    """

    id: str = "id"
    username: str = "username"
    password: str = "password"
    last_password_change_date: str = "last_password_change_date"
    sending_schedule: str = "sending_schedule"
    sending_time: str = "sending_time"
    whatsapp_number: str = "whatsapp_number"
    phone_number: str = "phone_number"
    email: str = "email"


USERS_DATA_COLUMNS = UsersDataColumns()


@dataclass
class FeedsDataColumns:
    """
    The FeedsDataColumns for FEEDS_DATA_COLUMNS modifying.
    contains the names of columns in the feeds data table.

    Object Attributes:
        id (str): Name of the feeds id column.
        links (str): Name of the feeds links column.
        rating (str): Name of ratings column.

    Examples:
        >>> my_feeds_data_attributes = FeedsDataColumns()
        >>> my_feeds_data_attributes.links_column
        url
        >>> my_feeds_data_attributes.links_column = "link"
        >>> my_feeds_data_attributes.links_column
        link
    """

    id: str = "id"
    link: str = "url"
    rating: str = "rating"


FEEDS_DATA_COLUMNS = FeedsDataColumns()


@dataclass
class SubscriptionsDataColumns:
    """
    The SubscriptionsDataColumns for SUBSCRIPTIONS_DATA_COLUMNS modifying.
    contains the names of the columns in subscriptions data table.

    Object Attributes:
        id (str): Name of the subscriptions id's column.
        user_id (str): Name of users id's column.
        feeds_id (str): Name of feeds id's column.

    Examples:
        >>> my_subscription_data_attributes = SubscriptionsDataColumns()
        >>> my_subscription_data_attributes.id
        id
        >>> my_subscription_data_attributes.user_id = "id_of_users"
        >>> my_subscription_data_attributes.user_id
        id_of_users
    """

    id: str = "id"
    user_id: str = "user_id"
    feed_id: str = "feed_id"


SUBSCRIPTIONS_DATA_COLUMNS = SubscriptionsDataColumns()

PASSWORD_ENCODING_METHOD: str | None = "utf-8"

RAPID_API_KEY: str | None = None
HTTPS_PREFIX: str = "https://"
RAPID_APIS_URL_SUFFIX: str = "p.rapidapi.com"
WHATSAPP_CHECKER_RAPID_NAME: str = "whatsapp-checker-pro"
WHATSAPP_EXISTENCE_CHECKER_URL_PREFIX: str = (
    f"{HTTPS_PREFIX + WHATSAPP_CHECKER_RAPID_NAME}.{RAPID_APIS_URL_SUFFIX}"
)
VERIPHONE_RAPID_NAME: str = "veriphone"
VERIPHONE_VALIDATOR_URL: str = (
    f"{HTTPS_PREFIX+VERIPHONE_RAPID_NAME}.{RAPID_APIS_URL_SUFFIX}/verify"
)
EMAIL_VERIFY_RAPID_NAME = "mailcheck"
EMAIL_VERIFY_URL = f"{HTTPS_PREFIX + EMAIL_VERIFY_RAPID_NAME}.{RAPID_APIS_URL_SUFFIX}/"


def create_rapidAPI_request_headers(api_name: str) -> Dict[str, str]:
    """Creates an headers dictionary for rapid API requests,'
    accordance to the specified API name.

    Args:
        api_name (str): The name of the specific API in rapid platform.

    Returns:
        Dict[str, str]: The headers dictionary for rapid API requests,
        so it can be used for requests library request.
    """
    return {
        "content-type": "application/octet-stream",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": f"{api_name}.{RAPID_APIS_URL_SUFFIX}",
    }
