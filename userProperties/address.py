"""An implementation for creating and updating Address object for users.
"""

from abc import ABC, abstractmethod


import config


class Address(ABC):
    """An abstract class for an digital address like Email, Phone or Whatsapp"""
    def __init__(self, address: str) -> None:
        self.address: str = address
        if not self._is_valid():
            raise ValueError(f"Invalid input: {address}")

    @abstractmethod
    def _is_valid(self) -> bool:
        pass

class WhatsAppAddress(Address):
    """concrete class for an whatsapp numbers"""
    def __init__(self, whatsapp_number: str):
        super().__init__(whatsapp_number)
        self.db_idx = config.USERS_DATA_COLUMNS.whatsapp_number
    def _is_valid(self) -> bool:
        pass

class PhoneAddress(Address):
    """concrete class for an phone numbers"""
    def __init__(self, phone_number: str):
        super().__init__(phone_number)
        self.db_idx = config.USERS_DATA_COLUMNS.phone_number
    def _is_valid(self) -> bool:
        pass

class EmailAddress(Address):
    """concrete class for an Email addresses"""
    def __init__(self, email: str):
        super().__init__(email)
        self.db_idx = config.USERS_DATA_COLUMNS.email
    def _is_valid(self) -> bool:
        pass


class AddressFactory:
    """Factory for creating address objects from an address string"""
    @staticmethod
    def create(address: str) -> Address:
        """Creates a new address.

        Args:
            address (str): An address of any type that inherits from the Address abstract class.

        Returns:
            Address: A custom address object.
        """
        pass