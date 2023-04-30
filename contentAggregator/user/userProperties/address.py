"""An implementation for creating and updating Address object for users.
"""
# TODO loss implementation

from __future__ import annotations
from abc import ABC, abstractmethod
import json
import re

import phonenumbers

from contentAggregator import config, webRequests


class Address(ABC):
    """An class for an digital / physical address like Email, Phone or Whatsapp
    can't be instantiated directly"""

    def __init__(
        self,
        address: str | phonenumbers.PhoneNumber,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ) -> None:
        self.address = address
        self.is_verified_flag = is_verified_flag
        if not is_valid_flag and not self._is_valid():
            cls_name = type(self).__name__
            raise ValueError(
                f"Invalid {cls_name} {self.address}, please enter a valid {cls_name}."
            )

    def __eq__(self, other: Address) -> bool:
        return self.address == other.address

    def __hash__(self) -> int:
        return hash(self.address)

    @abstractmethod
    def _is_valid(self) -> bool:
        """Check if the address is a valid address by it's type,
        performed by overrides.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        pass

    @abstractmethod
    def verify(self) -> None:
        """Verifies this address, by verification session with self.address"""
        pass

    @abstractmethod
    def send_message(self, message: str) -> None:
        pass


class NumberAddress(Address):
    """A middle class bet ween Address and it's fool implementors.
    Intended for numbers subscriptions.
    can't be instantiated directly."""

    def __new__(cls, *args, **kwargs):
        if cls is NumberAddress:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __init__(
        self,
        phone_number: str,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ):
        number_obj: phonenumbers.PhoneNumber = phonenumbers.parse(phone_number)
        super().__init__(number_obj, is_valid_flag, is_verified_flag)

    def _is_valid(self) -> bool:
        """Check if a self.number is also valid number for a particular region.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        # TODO after it will be enabled by netfree consider using phonenumbervalidatefree.p.rapidapi.com
        # it giving 500 requests / month.
        response = webRequests.get_response(
            method="get",
            url=config.VERIPHONE_VALIDATOR_URL,
            headers=config.create_rapidAPI_request_headers(config.VERIPHONE_RAPID_NAME),
            params={
                "phone": f"+{self.address.country_code}{self.address.national_number}"
            },
        )
        return json.loads(response).get("phone_valid", None)

    # Undecorated as abstractmethod, because has no effect
    # [this class can not inherit from ABC only, must be inherited from Address also]
    # this why we need the __new__ special method to prevent directly instantiating.


class WhatsAppAddress(NumberAddress):
    """Class for an whatsapp number"""

    def _is_valid(self) -> bool:
        """Check if a number is a valid and if it is a registered whatsapp number.

        Returns:
            bool: True if the whatsapp number is valid, False otherwise.
        """
        if not super()._is_valid():
            return False
        # TODO after it will be enabled by netfree consider using of Whatsapp Validator Fast Rapidapi,
        # TODO https://rapidapi.com/6782689498/api/whatsapp-validator-fast/pricing which is giving 50 requests per day for free
        response = webRequests.get_response(
            method="get",
            url=config.WHATSAPP_EXISTENCE_CHECKER_URL_PREFIX
            + str(self.address.country_code)
            + str(self.address.national_number),
            headers=config.create_rapidAPI_request_headers(
                config.WHATSAPP_CHECKER_RAPID_NAME
            ),
        )
        return "not" not in json.loads(response).get("response", None)

    def verify(self) -> None:
        """Verifies this whatsapp number, by verification session with self.address."""
        pass  # TODO

    def send_message(self, message: str) -> None:
        pass


class PhoneAddress(NumberAddress):
    """Class for a "phone addresses", used for kosher devices, for example [by voice calls]"""

    def verify(self) -> bool:
        pass  # TODO

    def send_message(self, message: str) -> None:
        pass


class SMSAddress(NumberAddress):
    """class for SMS addresses  - Hopefully it will be developed later"""

    pass
    # need to implement: __init__ method like in it's siblings,
    # is_valid staticmethod and return NumberAddress.is_valid(number)
    # + another condition if it's can receive SMS messages.
    # need to update the users table for new column called "sms_number".


class EmailAddress(Address):
    """class for an E-Mail addresses"""
    
    def _is_valid(self) -> bool:
        """Check if e-mail domain is valid, or a disposable/temporary address.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        if not re.match(config.EMAIL_ADDRESS_PATTERN, self.address):
            return False
        response = webRequests.get_response(
            method="get",
            url=config.EMAIL_VERIFY_URL,
            headers=config.create_rapidAPI_request_headers(
                config.EMAIL_VERIFY_RAPID_NAME
            ),
            params={"domain": self.address},
        )
        data = json.loads(response)
        return data.get("valid", False) and not data.get("disposable", True)

    def verify(self) -> bool:
        pass  # TODO

    def send_message(self, message: str) -> None:
        pass


class AddressFactory:
    """Factory for creating address objects from an address string"""

    @staticmethod
    def create(address_type: str, address: str) -> Address:
        """Creates a new trust address.

        Args:
            address_type (str): The type of the address.
            address (str): An address of any type that inherits from the Address abstract class.

        Returns:
            Address: A custom address object.
        """
        match address_type:
            case config.ADDRESSES_KEYS.whatsapp:
                return WhatsAppAddress(address, True, True)
            case config.ADDRESSES_KEYS.phone:
                return PhoneAddress(address, True, True)
            case config.ADDRESSES_KEYS.email:
                return EmailAddress(address, True, True)
            # case config.ADDRESSES_KEYS.sms:
            #     return SMSAddress(address, True, True)
