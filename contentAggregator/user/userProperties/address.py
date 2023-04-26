"""An implementation for creating and updating Address object for users.
"""
# TODO loss implementation

from __future__ import annotations
from abc import ABC, abstractmethod
import json

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

    # Intended: for allowing management of addresses set without multiplications.
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
        """Verifies this address, by verification session with self.address
        """
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

    def __init__(
        self,
        whatsapp_number: str,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ):
        super().__init__(whatsapp_number, is_valid_flag, is_verified_flag)
        self.db_idx = config.USERS_DATA_COLUMNS.whatsapp_number

    def _is_valid(self) -> bool:
        """Check if a number is a valid and if it is a registered whatsapp number.

        Returns:
            bool: True if the whatsapp number is valid, False otherwise.
        """
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
        return super()._is_valid and "not" not in json.loads(response).get(
            "response", None
        )

    def verify(self) -> None:
        """Verifies this whatsapp number, by verification session with self.address.
        """
        pass  # TODO

    def send_message(self, message: str) -> None:
        pass


class PhoneAddress(NumberAddress):
    """Class for a "phone addresses", used for kosher devices, for example [by voice calls]"""

    def __init__(
        self,
        phone_number: str,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ):
        super().__init__(phone_number, is_valid_flag, is_verified_flag)
        self.db_idx = config.USERS_DATA_COLUMNS.phone_number

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

    def __init__(
        self,
        email: str,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ):
        super().__init__(email, is_valid_flag, is_verified_flag)
        self.db_idx = config.USERS_DATA_COLUMNS.email

    def _is_valid(self) -> bool:
        """Check if e-mail domain is valid, or a disposable/temporary address.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        response = webRequests.get_response(
            method="get",
            url=config.EMAIL_VERIFY_URL,
            headers=config.create_rapidAPI_request_headers(
                config.EMAIL_VERIFY_RAPID_NAME
            ),
            params={"domain": self.address},
        )
        data = json.loads(response)
        return data.get('valid', False) and not data.get('disposable', True)

    def verify(self) -> bool:
        pass  # TODO

    def send_message(self, message: str) -> None:
        pass


class AddressFactory:
    """Factory for creating address objects from an address string"""

    @staticmethod
    def create(db_idx: str, address: str) -> Address:
        """Creates a new trust address.

        Args:
            db_idx (str): The index of this address to users table.
            address (str): An address of any type that inherits from the Address abstract class.

        Returns:
            Address: A custom address object.
        """
        match db_idx:
            case config.USERS_DATA_COLUMNS.whatsapp_number:
                return WhatsAppAddress(address, True, True)
            case config.USERS_DATA_COLUMNS.phone_number:
                return PhoneAddress(address, True, True)
            case config.USERS_DATA_COLUMNS.email:
                return EmailAddress(address, True, True)
