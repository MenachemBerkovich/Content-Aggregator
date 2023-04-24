"""An implementation for creating and updating Address object for users.
"""
# TODO loss implementation

from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
import json

import phonenumbers

from contentAggregator import config, webRequests


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

    @abstractproperty
    def is_valid(self) -> bool:
        """Check if the address is a valid address by it's type,
        performed by overrides.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        pass

    @abstractmethod
    def is_verified(self) -> bool:
        """Checks if self.address is verified by verification session.

        Returns:
            bool: True if self.address has been verified by the user as expected, False otherwise.
        """
        pass


class NumberAddress(Address):
    """A middle class bet ween Address and it's fool implementors.
    Intended for numbers subscriptions.
    can't be instantiated directly."""

    def __new__(cls, *args, **kwargs):
        if cls is Address:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __init__(self, phone_number: str):
        self.number: phonenumbers.PhoneNumber = phonenumbers.parse(self.address)
        self._is_valid_flag: bool | None = None

    @property
    def is_valid(self) -> bool:
        """Check if a self.number is also valid number for a particular region.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        return phonenumbers.is_valid_number(self.number)

    # Undecorated as abstractmethod, because has no effect
    # [this class can not inherit from ABC only, must be inherited from Address also]
    # this why we need the __new__ speciel method to prevent directly instantiating.
    def is_verified(self) -> bool:
        """Checks if self.address is verified by verification session.

        Returns:
            bool: True if self.address has been verified by the user as expected, False otherwise.
        """
        pass


class WhatsAppAddress(NumberAddress):
    """Class for an whatsapp number"""

    def __init__(self, whatsapp_number: str):
        super().__init__(whatsapp_number)
        self.db_idx = config.USERS_DATA_COLUMNS.whatsapp_number

    @property
    def is_valid(self) -> bool:
        """Check if a number is a valid and if it is a registered whatsapp number.

        Returns:
            bool: True if the whatsapp number is valid, False otherwise.
        """
        if self._is_valid_flag is None:
            self._is_valid_flag = (
                super().is_valid()
                and "not"
                not in json.loads(
                    webRequests.get_response(
                        method="get",
                        url=f"https://whatsapp-checker-pro.p.rapidapi.com/{str(self.number.country_code) + str(self.number.national_number)}",
                        headers={
                            "content-type": "application/octet-stream",
                            "X-RapidAPI-Key": config.RAPID_API_KEY,
                            "X-RapidAPI-Host": "whatsapp-checker-pro.p.rapidapi.com",
                        },
                    )
                )["response"]
            )
        return self._is_valid_flag

    def is_verified(self) -> bool:
        return None


class PhoneAddress(NumberAddress):
    """Class for an "phone addresses", used for kosher devices, for example [by voice calls]"""

    def __init__(self, phone_number: str):
        super().__init__(phone_number)
        self.db_idx = config.USERS_DATA_COLUMNS.phone_number

    def is_valid(self) -> bool:
        """Check if a number is a valid and can receive voice calls.

        Returns:
            bool: True if the number is valid by listed conditions, False otherwise.
        """
        return (
            super().is_valid() and "a" != "b"
        )  # TODO correct second condition for ability receive voice calls.
        # and check better the abilty of phonenumbers library to get info, or what does is_valid_number exactly


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

    def is_valid(self) -> bool:
        pass

    def is_verified(self) -> bool:
        return None


class AddressFactory:
    """Factory for creating address objects from an address string"""

    @staticmethod
    def create(db_idx: str, address: str) -> Address:
        """Creates a new address.

        Args:
            db_idx (str): The index of this address to users table.
            address (str): An address of any type that inherits from the Address abstract class.

        Returns:
            Address: A custom address object.
        """
        match db_idx:
            case config.USERS_DATA_COLUMNS.whatsapp_number:
                return WhatsAppAddress(address)
            case config.USERS_DATA_COLUMNS.phone_number:
                return PhoneAddress(address)
            case config.USERS_DATA_COLUMNS.email:
                return EmailAddress(address)
