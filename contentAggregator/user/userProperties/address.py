"""An implementation for creating and updating Address object for users.
"""
# TODO loss implementation

from __future__ import annotations
from abc import ABC, abstractmethod

import phonenumbers

from contentAggregator import config

class Address(ABC):
    """An class for an digital / physical address like Email, Phone or Whatsapp
    can't be instantiated directly"""

    def __init__(self, address: str) -> None:
        self.address: str = address

    # Intended: for allowing management of addresses set without multiplications.
    def __eq__(self, other: Address) -> bool:
        return self.address == other.address

    def __hash__(self) -> int:
        return hash(self.address)

    @abstractmethod
    def is_verified(self) -> bool:
        """Checks if self.address is verified by verification session.

        Returns:
            bool: True if self.address has been verified by the user as expected, False otherwise.
        """
        pass

class NumberAddress(Address, ABC):
    """A middle class bet ween Address and it's fool implementors.
    Intended for numbers subscriptions.
    can't be instantiated directly."""
    def __new__(cls, *args, **kwargs):
        if cls is Address:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    @staticmethod
    def is_valid(number: str) -> bool:
        """Check if a phone number is a valid phone number.

        Args:
            phone_number (str): The phone number to check.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        number_obj = phonenumbers.parse(number)
        return phonenumbers.is_valid_number(number_obj)

    @abstractmethod
    def is_verified(self) -> bool:
        """Checks if self.address is verified by verification session.

        Returns:
            bool: True if self.address has been verified by the user as expected, False otherwise.
        """
        pass

class WhatsAppAddress(NumberAddress):
    """Class for an whatsapp number"""
    def __init__(self, whatsapp_number: str):
        if not WhatsAppAddress.is_valid(whatsapp_number):
            raise ValueError("Invalid whatsapp number")
        super().__init__(whatsapp_number)
        self.db_idx = config.USERS_DATA_COLUMNS.whatsapp_number

    @staticmethod
    def is_valid(number: str) -> bool:
        """Check if a number is a valid and registered whatsapp number.

        Args:
            number (str): The whatsapp number to check.

        Returns:
            bool: True if the whatsapp number is valid, False otherwise.
        """
        return NumberAddress.is_valid(number) and "a"!="b" #TODO correct second condition for whatsapp account axistance.

    def is_verified(self) -> bool:
        return None

class PhoneAddress(NumberAddress):
    """Class for an "phone addresses", used for kosher devices [by voice calls]"""
    def __init__(self, phone_number: str):
        if not PhoneAddress.is_valid(phone_number):
            raise ValueError("Invalid phone number")
        super().__init__(phone_number)
        self.db_idx = config.USERS_DATA_COLUMNS.phone_number

    @staticmethod
    def is_valid(number: str) -> bool:
        """Check if a number is a valid and can receive voice calls.

        Args:
            number (str): The number to check.

        Returns:
            bool: True if the number is valid by listed conditions, False otherwise.
        """
        return NumberAddress.is_valid(number) and "a"!="b" #TODO correct second condition for ability receive voice calls.

class SMSAddress(NumberAddress):
    """class for SMS addresses  - Hopefully it will be developed later"""
    pass
    # need to implement: __init__ method like in it's siblings,
    # is_valid staticmethod and return NumberAddress.is_valid(number)
    # + another condition if it's can receive SMS messages.
    # need to update the users table for new column called "sms_number".

class EmailAddress(Address):
    """class for an E-Mail addresses"""
    def __init__(self, email: str):
        super().__init__(email)
        self.db_idx = config.USERS_DATA_COLUMNS.email

    @staticmethod
    def is_valid(address: str) -> bool:
        pass

    def is_verified(self) -> bool:
        return None


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