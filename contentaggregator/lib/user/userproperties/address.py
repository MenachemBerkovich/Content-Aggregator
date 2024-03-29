"""An implementation for creating Address object for users, and use it for messages sending.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import json
import re
from concurrent import futures

import phonenumbers
import yagmail

from contentaggregator.lib.feeds.feed import Feed
from contentaggregator.lib import config, webrequests, messagesgeneration


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
                f"Invalid {cls_name} {repr(self.address)}, please enter a valid {cls_name}."
            )

    def __eq__(self, other: Address) -> bool:
        return self.address == other.address and type(self) == type(other)

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
    def send_message(self, *feeds: Feed) -> None:
        """Sends messages to self.address from system address.
        It's expected to get kwargs as parameters, each concrete method as it's requirements.
        """
        pass


class NumberAddress(Address):
    """A middle class between Address and it's fool implementors.
    Intended for numbers subscriptions.
    can't be instantiated directly."""

    def __new__(cls, *args, **kwargs):
        # Temporary
        if cls is SMSAddress:
            raise NotImplementedError("SMS numbers are not supported yet.")
        # Regular
        elif cls is NumberAddress:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __init__(
        self,
        phone_number: str,
        is_valid_flag: bool = False,
        is_verified_flag: bool | None = None,
    ):
        number_obj: phonenumbers.PhoneNumber = phonenumbers.parse(phone_number)
        super().__init__(
            f"+{str(number_obj.country_code)}{str(number_obj.national_number)}",
            is_valid_flag,
            is_verified_flag,
        )

    def _is_valid(self) -> bool:
        """Check if a self.number is also valid number for a particular region.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        # TODO after it will be enabled by netfree consider using phonenumbervalidatefree.p.rapidapi.com
        # it giving 500 requests / month.
        response = webrequests.get_response(
            method="get",
            url=config.VERIPHONE_VALIDATOR_URL,
            headers=config.create_rapidAPI_request_headers(config.VERIPHONE_RAPID_NAME),
            params={"phone": self.address},
        )
        return bool(json.loads(response.text).get("phone_valid", None))

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
        response = webrequests.get_response(
            method="get",
            url=config.WHATSAPP_VALIDATOR_URL,
            headers=config.create_rapidAPI_request_headers(
                config.WHATSAPP_VALIDATOR_NAME
            ),
            params={"phone": self.address[1:]},
        )
        return json.loads(response.text).get("valid", None)

    def send_message(self, *feeds: Feed) -> None:
        """Sends a message to whatsapp number.

        Args:
            message_params (str): Necessary params for specific message,
            like (content='Hey I am content aggregator...', image='url_or_file_path',
            audio='audio_url_or_file_path', video='video_url_or_file_path')
        """
        pass


class PhoneAddress(NumberAddress):
    """Class for a "phone addresses", used for kosher devices, for example [by voice calls]"""

    def send_message(self, *feeds: Feed) -> None:
        """Sends a voice message to the phone number.

        Args:
            feeds_content (str): variable number of feed items lists.
        """
        pass


class SMSAddress(NumberAddress):
    """class for SMS addresses  - Hopefully it will be developed later"""

    def _is_valid(self) -> bool:
        raise NotImplementedError("SMS addresses are not supported yet(:")

    def send_message(self, *feeds: Feed) -> None:
        pass

    # need to implement: __init__ method like in it's siblings,
    # is_valid staticmethod and return NumberAddress.is_valid(number)
    # + another condition if it's can receive SMS messages.


class EmailAddress(Address):
    """class for an E-Mail addresses"""

    def _is_valid(self) -> bool:
        """Check if e-mail domain is valid, or a disposable/temporary address.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        if not re.match(config.EMAIL_ADDRESS_PATTERN, self.address):
            return False
        response = webrequests.get_response(
            method="get",
            url=config.EMAIL_VERIFY_URL,
            headers=config.create_rapidAPI_request_headers(
                config.EMAIL_VERIFY_RAPID_NAME
            ),
            params={"domain": self.address},
        )
        data = json.loads(response.text)
        return data.get("valid", False) and not data.get("disposable", True)

    def send_message(self, *feeds: Feed) -> None:
        """Sends a message to email address.

        Args:
            feeds (str): variable number of feeds.
        """
        # message = ""
        # message = "\n".join(
        #     messagesgeneration.generate_html_feed_summery(feed) for feed in feeds
        # )
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            threaded_tasks = [
                executor.submit(messagesgeneration.generate_html_feed_summery, feed)
                for feed in feeds
            ]
            message = "\n".join(
                completed_task.result()
                for completed_task in futures.as_completed(threaded_tasks)
            )
        with yagmail.SMTP(config.EMAIL_SENDER_ADDRESS) as yag:
            yag.send(
                to=self.address,
                subject="Hi! Here's is BerMen:)",
                contents=message,
            )


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
            case config.ADDRESSES_KEYS.sms:
                return SMSAddress(address, True, True)
