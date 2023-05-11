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
        last_password_change_date (str): Name column contains the date in which the last password change is made.
        addresses (str): Name of the addresses column [contains a dict of addresses, as a json string]
        subscriptions (str): Name of the subscriptions column [contains a list of the user subscriptions as a json string]
        sending_schedule (str): Name of the sending_schedule column, It will contain a number of Enum class, represents if weekly or daily.
        sending_time (str): Name of the sending_time column, It will contain the time of sending.

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
    addresses: str = "addresses"
    subscriptions: str = "subscriptions"
    sending_schedule: str = "sending_schedule"
    sending_time: str = "sending_time"


USERS_DATA_COLUMNS = UsersDataColumns()

@dataclass
class AddressesKeys:
    """The UsersDataColumns for USERS_DATA_COLUMNS modifying.
    contains the names of columns in the user data table.

    Object Attributes:
        email (str): Key for email address inside dictionary
        phone (str): Key for phone number inside dictionary.
        sms (str): Key for SMS number inside dictionary.
        whatsapp (str): Key for WhatsApp number inside dictionary.
    """
    email: str = "email"
    phone: str = "phone"
    sms: str = "sms"
    whatsapp: str = "whatsapp"
    
ADDRESSES_KEYS = AddressesKeys()


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
        >>> my_feeds_data_attributes.link
        url
        >>> my_feeds_data_attributes.link = "link"
        >>> my_feeds_data_attributes.link
        link
    """

    id: str = "id"
    link: str = "url"
    rating: str = "rating"
    feed_type: str = "type" #TODO new column in db
    categories: str = "categories" # TODO new column in db type JSON

FEEDS_DATA_COLUMNS = FeedsDataColumns()

@dataclass
class FeedCategoriesNames:
    """Defines the feed categories names in the database.
    """

    news: str = "news"
    blogs: str = "blogs"
    travel: str = "travel"
    technology: str = "technology"

FEEDS_CATEGORIES_NAMES = FeedCategoriesNames()


@dataclass
class FeedTypes:
    """
    The FeedTypes allowed in FeedsDataColumns.type column.
    contains the names of feed types.

    Object Attributes:
        html (str): Name of the HTML feed type.
        rss (str): Name of the XML feed type.
    """
    html: str = 'HTML Feed'
    xml: str = 'RSS Feed'  # feed types such as RSS, CDF and Atom.

FEED_TYPES = FeedTypes()

PASSWORD_ENCODING_METHOD: str | None = "utf-8"

RAPID_API_KEY: str | None = None
HTTPS_PREFIX: str = "https://"
RAPID_APIS_URL_SUFFIX: str = "p.rapidapi.com"
WHATSAPP_VALIDATOR_NAME: str = "whatsapp-validator-fast"
WHATSAPP_VALIDATOR_URL: str = (
    f"{HTTPS_PREFIX + WHATSAPP_VALIDATOR_NAME}.{RAPID_APIS_URL_SUFFIX}/whatsapp/valid"
)
VERIPHONE_RAPID_NAME: str = "veriphone"
VERIPHONE_VALIDATOR_URL: str = (
    f"{HTTPS_PREFIX+VERIPHONE_RAPID_NAME}.{RAPID_APIS_URL_SUFFIX}/verify"
)

EMAIL_ADDRESS_PATTERN = r"^[a-zA-Z0-9._%+-]+@(?!.*\.{2,})([a-zA-Z0-9]+([.-]?[a-zA-Z0-9]+)*)\.([a-zA-Z]{2,})$"
EMAIL_VERIFY_RAPID_NAME = "mailcheck"
EMAIL_VERIFY_URL = f"{HTTPS_PREFIX + EMAIL_VERIFY_RAPID_NAME}.{RAPID_APIS_URL_SUFFIX}/"
EMAIL_SENDER_ADDRESS: str | None = 'bermen.system@gmail.com' #TODO register it with keyring and configure the app password in the main file that runs messenger.
# when is will enabled to make 2-step authentication for this google account.
EMAIL_SENDER_PWD: str | None = None

def create_rapidAPI_request_headers(api_name: str) -> Dict[str, str]:
    """Creates an headers dictionary for rapid API requests,'
    accordance to the specified API name.

    Args:
        api_name (str): The name of the specific API in rapid platform.

    Returns:
        Dict[str, str]: The headers dictionary for rapid API requests,
        so it can be used for requests library request.
    """
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": f"{api_name}.{RAPID_APIS_URL_SUFFIX}",
    }
    if api_name != WHATSAPP_VALIDATOR_NAME:
        headers["content-type"] = "application/octet-stream"
    return headers
