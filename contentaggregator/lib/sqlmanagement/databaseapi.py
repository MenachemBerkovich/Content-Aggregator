"""
Functions collection for some custom SQL queries required for the system.
"""

from typing import List, Tuple, Iterable, Any, Dict, Union, Set

from .databasecursor import MySQLCursorCM
from contentaggregator.lib import config
# from contentaggregator.lib.feeds import feed


def select(
    *,
    cols: str | Iterable[str] = "*",
    table: str,
    condition_expr: str | None = None,
    desired_rows_num: int | None = None,
) -> List[Tuple[Any, ...]]:
    """Select the desired columns and rows
    from the specified table in the database defined by MySQLCursorCM class.

    Args:
        table (str): The name of the table(s) to select from.
        cols (str | Iterable[str], optional): The name(s) of the specified columns to select them.
                                              Defaults to "*".
        condition_expr (str | None, optional): Condition to select by,
                                          Defaults to None
                                          [has no effect if it's not required by the caller].
        desired_rows_num (int): The desired number of rows.

    Returns:
        List[Tuple[str, ...]]: A list with the desired rows as tuples.
    """
    if isinstance(cols, Union[Tuple, List]):
        cols = ", ".join(cols)
    query_str = f"SELECT {cols} FROM {table}"
    if condition_expr:
        query_str += f" WHERE BINARY {condition_expr}"
    print(query_str)
    with MySQLCursorCM() as cursor:
        cursor.execute(query_str)
        return (
            cursor.fetchmany(size=desired_rows_num)
            if desired_rows_num
            else cursor.fetchall()
        )


def insert(
    *,
    table: str,
    cols: str | Iterable[str],
    condition_expr: str | None = None,
    values: Any | Iterable[Any],
) -> int | None:
    """Insert a new data to the desired location in the database.

    Args:
        table (str): The name of the table to be inserted into.
        cols (str | Iterable[str]): The name(s) of the specified column(s) to be inserted into.
        values (Any | Iterable[Any]): The new value(s) to be inserted.
        condition_expr (str | None, optional): Condition on the insertion. Defaults to None.
    Returns:
        int | None: The row id of the inserted value, Or None it is unavailable.
    """
    values_expr_preparing = "%s"
    if isinstance(cols, Iterable):
        values_expr_preparing = ",".join("%s" for _ in range(len(cols)))
        cols = ", ".join(cols)
    query_str = f"INSERT INTO {table} ({cols}) VALUES ({values_expr_preparing})"
    if condition_expr:
        query_str += f" WHERE {condition_expr}"
    print(query_str, values)

    with MySQLCursorCM() as cursor:
        cursor.execute(query_str, values)
        return cursor.lastrowid


def update(
    *, table: str, updates_dict: Dict[Any, Any], condition_expr: str | None = None
) -> None:
    """Update the desired table with the given updates dict, and according to condition if exists.

    Args:
        table (str): The name of the table to be updated.
        updates_dict (Dict[Any, Any]): Dictionary of columns names as keys and the new updated values as values.
        condition_expr (str | None, optional): Condition on the update locations. Defaults to None.
    """
    updates = ", ".join(
        f"{k} = {v}" if v is not None else f"{k} = NULL"
        for k, v in updates_dict.items()
    )
    # updates = ", ".join(f"%({key})s" for key in updates_dict)
    query_str = f"UPDATE {table} SET {updates}"
    if condition_expr:
        query_str += f" WHERE {condition_expr}"
    print(query_str, updates_dict)
    with MySQLCursorCM() as cursor:
        cursor.execute(query_str)  # , updates_dict)


def delete(*, table: str, condition_expr: str | None = None) -> int | None:
    """Delete rows from the given table, when condition is True (if condition_expr is not None).

    Args:
        table (str): The table to delete from.
        condition_expr (str | None, optional): Condition - which rows will be deleted.
                                               Defaults to None.

    Returns:
        int | None: The number of the rows affected by the delete operation,
                    or None this data is not available.
    """
    query_str = f"DELETE FROM {table}"
    if condition_expr:
        query_str += f" WHERE {condition_expr}"
    with MySQLCursorCM() as cursor:
        cursor.execute(query_str)
        cursor.fetchone()
        return cursor.rowcount


def get_users_set() -> Set[int] | None:
    # TODO with threads
    """Collects all users id's and returns them as a set of ints.

    Returns:
        Set[int] | None: A set of user's id's if there is any users, None otherwise.
    """
    db_response = select(
        cols=config.USERS_DATA_COLUMNS.id,
        table=config.DATABASE_TABLES_NAMES.users_table,
    )
    return {user[0] for user in db_response} if db_response[0][0] else None


def get_feeds_set() -> List[Tuple[int | str]]:
    # TODO with threads
    """Collects all feeds existing in the database
    and returns them as a set of feeds objects.

    Returns:
        List[Tuple[int | str]]: A list of tuples, where each one,
        holds feed id and feed type.
    """
    return select(
        cols=[config.FEEDS_DATA_COLUMNS.id, config.FEEDS_DATA_COLUMNS.feed_type],
        table=config.DATABASE_TABLES_NAMES.feeds_table,
    )
