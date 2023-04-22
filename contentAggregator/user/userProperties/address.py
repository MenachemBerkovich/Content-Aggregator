"""An implementation for creating and updating Address object for users.
"""

from __future__ import annotations
from abc import ABC, abstractmethod

from contentAggregator import config

class AddressDataManager(ABC):
    """An abstract class for an digital address like Email, Phone or Whatsapp"""
    def __init__(self, address: str) -> None:
        self.address: str = address
        if not self._is_valid():
            raise ValueError(f"Invalid input: {address}")

    @abstractmethod
    def _is_valid(self) -> bool:
        pass

    # Intended: for allowing management of addresses set without multiplications.
    def __eq__(self, other: AddressDataManager) -> bool:
        return self.address == other.address

    def __hash__(self) -> int:
        return hash(self.address)


class WhatsAppAddressDataManager(AddressDataManager):
    """concrete class for an whatsapp numbers"""
    def __new__(cls, whatsapp_number: str) -> object:
        # Intended for instance.__class__.__name__ call.
        # To avoid print of 'DataManager' in string output.
        cls.__name__ = "WhatsAppAddress"
        return super().__new__(cls, whatsapp_number, (), {})

    def __init__(self, whatsapp_number: str):
        super().__init__(whatsapp_number)
        self.db_idx = config.USERS_DATA_COLUMNS.whatsapp_number

    def _is_valid(self) -> bool:
        pass

class PhoneAddressDataManager(AddressDataManager):
    """concrete class for an phone numbers"""
    def __new__(cls, phone_number: str) -> object:
        # Intended for instance.__class__.__name__ call.
        # To avoid print of 'DataManager' in string output.
        # Needed in collections.UserCollectionResetController.__iadd__ and __isub__ methods.
        cls.__name__ = "PhoneAddress"
        return super().__new__(cls, phone_number, (), {})

    def __init__(self, phone_number: str):
        super().__init__(phone_number)
        self.db_idx = config.USERS_DATA_COLUMNS.phone_number

    def _is_valid(self) -> bool:
        pass

class EmailAddressDataManager(AddressDataManager):
    """concrete class for an Email addresses"""
    def __new__(cls, email: str) -> object:
        # Intended for instance.__class__.__name__ call.
        # To avoid print of 'DataManager' in string output.
        # Needed in collections.UserCollectionResetController.__iadd__ and __isub__ methods.
        cls.__name__ = "EmailAddress"
        return super().__new__(cls, email, (), {})

    def __init__(self, email: str):
        super().__init__(email)
        self.db_idx = config.USERS_DATA_COLUMNS.email

    def _is_valid(self) -> bool:
        pass


class AddressFactory:
    """Factory for creating address objects from an address string"""
    @staticmethod
    def create(address: str) -> AddressDataManager:
        """Creates a new address.

        Args:
            address (str): An address of any type that inherits from the Address abstract class.

        Returns:
            Address: A custom address object.
        """
        pass