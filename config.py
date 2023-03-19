"""
This is the configuration file for allowing other users to define their own configuration
like data base credentials, database name, data tables name and columns of data tables.
"""


SQL_USERNAME: str | None = None

SQL_HOST: str | None = None

SQL_PASSWORD: str | None = None

DATABASE_NAME: str | None = None

from dataclasses import dataclass

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
    users_table: str = "users_information"
    feeds_table: str = "feeds_information"
    subscriptions_table: str = "subscriptions_information"

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
    password: str = "password_hash_value"

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
    links: str = "url"
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
