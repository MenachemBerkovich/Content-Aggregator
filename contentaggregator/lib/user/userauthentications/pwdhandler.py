"""Handles the encryption and comparison of the passwords.
"""

import bcrypt

from contentaggregator.lib import config

def encrypt_password(password: str) -> bytes:
    """Encrypt the password using bcrypt.

    Args:
        password (str): The original password to be encrypted.

    Returns:
        bytes: The encrypted password.
    """
    return bcrypt.hashpw(
        password.encode(config.PASSWORD_ENCODING_METHOD), bcrypt.gensalt()
    )


def is_same_password(original_password: str, hashed_password: bytes) -> bool:
    """Check if the original_password is the same
    with the hashed_password that stored in the database.

    Args:
        original_password (str): The password in a plain text format.
        hashed_password (bytes): The password in hashed format.

    Returns:
        bool: True if they are the same password, False otherwise.
    """
    return bcrypt.checkpw(
        original_password.encode(config.PASSWORD_ENCODING_METHOD),
        hashed_password,
    )
