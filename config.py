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

DATABASE_TABLES_NAMES = TablesNames()

@dataclass
class UsersDataColumns:
    """
    The UsersDataColumns for USERS_DATA_COLUMNS modifying.
    contains the names of columns in the user data table.
    
    Object Attributes:
        user_id_column (str): Name of the id column.
        username_column (str): Name of usernames column.
        password_column (str): Name of the password hash value column.
        favorites_column (str): Name of the favorites feeds column.
        
    Examples:
        >>> my_user_data_attributes = UsersDataColumns()
        >>> my_tables.user_id
        id
        >>> my_user_data_attributes.user_id_column = "id_columns"
        >>> my_user_data_attributes.user_id_column
        id_columns
    """
    user_id_column: str = "id"
    username_column: str = "username"
    password_column: str = "password_hash_value"
    favorites_column: str = "favorites_feeds"

USERS_DATA_COLUMNS = UsersDataColumns()

@dataclass
class FeedsDataColumns:
    """
    The FeedsDataColumns for FEEDS_DATA_COLUMNS modifying.
    contains the names of columns in the feeds data table.
    
    Object Attributes:
        links_column (str): Name of the links column.
        rating_column (str): Name of ratings column.
        
    Examples:
        >>> my_feeds_data_attributes = FeedsDataColumns()
        >>> my_feeds_data_attributes.links_column
        url
        >>> my_feeds_data_attributes.links_column = "link"
        >>> my_feeds_data_attributes.links_column
        link
    """
    links_columns: str = "url"
    rating_column: str = "rating"

FEEDS_DATA_COLUMNS = FeedsDataColumns()
