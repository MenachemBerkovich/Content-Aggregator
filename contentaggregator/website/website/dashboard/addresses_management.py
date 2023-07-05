"""User's addresses management and presentation.
"""

import pynecone as pc

from contentaggregator.lib import config
from contentaggregator.lib.user.userproperties import collections, address
from . import entrance


def get_address_type_name(address_key: str) -> str:
    """Get the address type for a given address key,
    so it will be available to construct the address object by the accordance class name.

    Args:
        address_key (str): The key of the address object, should be: 'email', 'sms', etc.

    Returns:
        str: The name of the exact match class.
    """
    match address_key:
        case config.ADDRESSES_KEYS.email:
            return "EmailAddress"
        case config.ADDRESSES_KEYS.whatsapp:
            return "WhatsAppAddress"
        case config.ADDRESSES_KEYS.sms:
            return "SMSAddress"
        case config.ADDRESSES_KEYS.phone:
            return "PhoneAddress"


class AddressesDashboardState(entrance.EntranceState):
    """User addresses dashboard manager."""

    new_email_address: str = ""
    email_address_reset_message: str = ""
    new_phone_address: str = ""
    phone_address_reset_message: str = ""
    new_whatsapp_address: str = ""
    whatsapp_address_reset_message: str = ""
    new_sms_address: str = ""
    sms_address_reset_message: str = ""

    @pc.var
    def is_some_address_missing(self) -> bool:
        """A ComputedVar that indicates if some address is missing.

        Returns:
            bool: True if some address is missing, False otherwise.
        """
        return not all(
            [
                self.email_address,
                self.sms_address,
                self.whatsapp_address,
                self.phone_address,
            ]
        )

    @pc.var
    def has_no_email_address(self) -> bool:
        """A ComputedVar that indicates if current self._user is unregistered at email address.

        Returns:
            bool: True if has no, False otherwise.
        """
        return not bool(self.email_address)

    @pc.var
    def has_no_whatsapp_address(self) -> bool:
        """A ComputedVar that indicates if self._user is unregistered at whatsapp address.

        Returns:
            bool: True if has no, False otherwise.
        """
        return not bool(self.whatsapp_address)

    @pc.var
    def has_no_sms_address(self) -> bool:
        """A ComputedVar that indicates if self._user is unregistered at sms address.

        Returns:
            bool: True if has no, False otherwise.
        """
        return not bool(self.sms_address)

    @pc.var
    def has_no_phone_address(self) -> bool:
        """A ComputedVar that indicates if self._user is unregistered at phone number address.

        Returns:
            bool: True if has no, False otherwise.
        """
        return not bool(self.phone_address)

    @pc.var
    def has_email_address(self) -> bool:
        """A ComputedVar that indicates if self._user is registered at email address.

        Returns:
            bool: True if there is, False otherwise.
        """
        return bool(self.email_address)

    @pc.var
    def has_sms_address(self) -> bool:
        """A ComputedVar that indicates if self._user is registered at sms address.

        Returns:
            bool: True if there is, False otherwise.
        """
        return bool(self.sms_address)

    @pc.var
    def has_phone_address(self) -> bool:
        """A ComputedVar that indicates if self._user is registered at phone number.

        Returns:
            bool: True if there is, False otherwise.
        """
        return bool(self.phone_address)

    @pc.var
    def has_whatsapp_address(self) -> bool:
        """A ComputedVar that indicates if self._user is registered at whatsapp number.

        Returns:
            bool: True if there is, False otherwise.
        """
        return bool(self.whatsapp_address)

    def reset_address(self, address_key: str, by_new_address: bool = True) -> None:
        """Reset the self.{address_key}_address,
        to the new_address or to empty string,
        as a dependency of by_new_address var.

        Args:
            address_key (str): The address key of the attribute.
            by_new_address (bool, optional): If to reset it to the existing self.new_{address_key}_address,
            or return it to the initial state - empty string. Defaults to True.
        """
        # self.__dict__[f'{address_key}_address'] = self.__dict__[f'new_{address_key}_address'] if by_new_address else "" - doesn't work.
        # it's does not update the members as expected - because it's these are parent class members, and maybe it's related to the implementation of the pynecone.State class.
        match address_key:
            case config.ADDRESSES_KEYS.email:
                self.email_address = self.new_email_address if by_new_address else ""
            case config.ADDRESSES_KEYS.whatsapp:
                self.whatsapp_address = (
                    self.new_whatsapp_address if by_new_address else ""
                )
            case config.ADDRESSES_KEYS.phone:
                self.phone_address = self.new_phone_address if by_new_address else ""
            case config.ADDRESSES_KEYS.sms:
                self.sms_address = self.new_sms_address if by_new_address else ""

    def reset_message(self, address_key: str, new_message: str = "") -> None:
        """Reset message of the given address, to the new message.

        Args:
            address_key (str): The address key of the requested address message.
            new_message (str, optional): The new message to reset to. Defaults to "".
        """
        # self.__dict__[f'{address_key}_message'] = new_message - will be work? - Not. see above.
        match address_key:
            case config.ADDRESSES_KEYS.email:
                self.email_address_reset_message = new_message
            case config.ADDRESSES_KEYS.whatsapp:
                self.whatsapp_address_reset_message = new_message
            case config.ADDRESSES_KEYS.phone:
                self.phone_address_reset_message = new_message
            case config.ADDRESSES_KEYS.sms:
                self.sms_address_reset_message = new_message

    def change_address(self, address_key: str) -> None:
        """Change specified user address.
        Add it to the self._user.addresses or modify an existing one.
        As a dependency of the address status -
        if it exist, then it will be modified, otherwise it will be added.

        Args:
            address_key (str): The key of the address change.
        """
        self.reset_message(address_key)
        class_name = get_address_type_name(address_key)
        if self._user:
            try:
                new_address_obj = address.__dict__[class_name](
                    self.__dict__[f"new_{address_key}_address"]
                )
                # If it is a new address for self._user, than add it.
                if (
                    self.has_addresses
                    and config.ADDRESSES_KEYS.__dict__[address_key]
                    not in self._user.addresses.collection
                ):
                    self._user.addresses += collections.UserDictController(
                        **{address_key: new_address_obj}
                    )
                # If it is an existing address, modify it
                elif self.has_addresses:
                    self._user.addresses.collection[
                        config.ADDRESSES_KEYS.__dict__[address_key]
                    ] = new_address_obj
                    # Update database.
                    # TODO Consider simplify it by adding email, whatsapp, sms and phone properties setters and getters
                    # Inside User class (if it's job?!), or inside UserDictController class (but how to access _update_addresses for database without circular importing?!)
                    self._user._update_addresses()
                    self.reset_message(address_key, "Address successfully updated!")
                # If user has no any address, set it's addresses attribute.
                else:
                    self._user.addresses = collections.UserDictController(
                        **{address_key: new_address_obj}
                    )
                    self.has_addresses = True
                self.reset_address(address_key)
            except Exception as e:
                self.reset_message(address_key, str(e))

    def get_current_address(self, address_key: str) -> str:
        """Returns the current address of the address_key [Foe self._user of course].

        Args:
            address_key (str): The key of the requested address.

        Returns:
            str: The current address of the address_key.
        """
        match address_key:
            case config.ADDRESSES_KEYS.email:
                return self.email_address
            case config.ADDRESSES_KEYS.whatsapp:
                return self.whatsapp_address
            case config.ADDRESSES_KEYS.sms:
                return self.sms_address
            case config.ADDRESSES_KEYS.phone:
                return self.phone_address

    def delete_address(self, address_key: str) -> None:
        """Delete a certain address from self._user.addresses.

        Args:
            address_key (str): The key of the address to delete.
        """
        self.reset_message(address_key)
        class_name = get_address_type_name(address_key)
        current_address = self.get_current_address(address_key)
        if self._user:
            try:
                new_address_obj = address.__dict__[class_name](
                    current_address, True, True
                )
                if self.has_addresses:
                    self._user.addresses -= collections.UserDictController(
                        **{address_key: new_address_obj}
                    )
                    self.reset_address(address_key, False)
            except Exception as e:
                self.reset_message(address_key, str(e))
            if not self._user.addresses:
                self.has_addresses = False


def user_addresses_view() -> pc.Component:
    """Generate a component view for a user's addresses.
    Also buttons for address deletion and modification.

    Returns:
        pc.Component: The component of addresses where user is registered.
    """
    return pc.vstack(
        pc.cond(
            AddressesDashboardState.has_email_address,
            pc.vstack(
                pc.hstack(
                    pc.text("Email Address:"),
                    pc.input(
                        default_value=AddressesDashboardState.email_address,
                        on_change=AddressesDashboardState.set_new_email_address,
                    ),
                    pc.button_group(
                        pc.button(
                            "Change",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.email
                            ),
                        ),
                        pc.button(
                            "Delete",
                            on_click=lambda _: AddressesDashboardState.delete_address(
                                config.ADDRESSES_KEYS.email
                            ),
                        ),
                        spacing=3,
                    ),
                ),
                pc.text(AddressesDashboardState.email_address_reset_message),
            ),
        ),
        pc.cond(
            AddressesDashboardState.has_whatsapp_address,
            pc.vstack(
                pc.hstack(
                    pc.text("Whatsapp Address:"),
                    pc.input(
                        default_value=AddressesDashboardState.whatsapp_address,
                        on_change=AddressesDashboardState.set_new_whatsapp_address,
                    ),
                    pc.button_group(
                        pc.button(
                            "Change",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.whatsapp
                            ),
                        ),
                        pc.button(
                            "Delete",
                            on_click=lambda _: AddressesDashboardState.delete_address(
                                config.ADDRESSES_KEYS.whatsapp
                            ),
                        ),
                        spacing=3,
                    ),
                ),
                pc.text(AddressesDashboardState.whatsapp_address_reset_message),
            ),
        ),
        pc.cond(
            AddressesDashboardState.has_sms_address,
            pc.vstack(
                pc.hstack(
                    pc.text("SMS Address:"),
                    pc.input(
                        default_value=AddressesDashboardState.sms_address,
                        on_change=AddressesDashboardState.set_new_sms_address,
                    ),
                    pc.button_group(
                        pc.button(
                            "Change",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.sms
                            ),
                        ),
                        pc.button(
                            "Delete",
                            on_click=lambda _: AddressesDashboardState.delete_address(
                                config.ADDRESSES_KEYS.sms
                            ),
                        ),
                        spacing=3,
                    ),
                ),
                pc.text(AddressesDashboardState.sms_address_reset_message),
            ),
        ),
        pc.cond(
            AddressesDashboardState.has_phone_address,
            pc.vstack(
                pc.hstack(
                    pc.text("Phone Number:"),
                    pc.input(
                        default_value=AddressesDashboardState.phone_address,
                        on_change=AddressesDashboardState.set_new_phone_address,
                    ),
                    pc.button_group(
                        pc.button(
                            "Change",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.phone
                            ),
                        ),
                        pc.button(
                            "Delete",
                            on_click=lambda _: AddressesDashboardState.delete_address(
                                config.ADDRESSES_KEYS.phone
                            ),
                        ),
                        spacing=3,
                    ),
                ),
                pc.text(AddressesDashboardState.phone_address_reset_message),
            ),
        ),
        border_radius="15px",
        padding=5,
        border_color="black",
        border_width="thick",
    )


def available_addresses_view() -> pc.Component:
    """Generate a component view for a non-user's addresses.
    Also buttons for address addition.

    Returns:
        pc.Component: The component of addresses where user is not registered yet.
    """
    return pc.vstack(
        pc.text("Available Addresses:", as_="b"),
        pc.vstack(
            pc.cond(
                AddressesDashboardState.has_no_email_address,
                pc.vstack(
                    pc.hstack(
                        pc.text("Email Address:"),
                        pc.input(
                            placeholder="Enter your email address...",
                            on_change=AddressesDashboardState.set_new_email_address,
                        ),
                        pc.button(
                            "Add",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.email
                            ),
                        ),
                    ),
                    pc.text(AddressesDashboardState.email_address_reset_message),
                ),
            ),
            pc.cond(
                AddressesDashboardState.has_no_whatsapp_address,
                pc.vstack(
                    pc.hstack(
                        pc.text("Whatsapp Address:"),
                        pc.input(
                            placeholder="Enter your whatsapp address...",
                            on_change=AddressesDashboardState.set_new_whatsapp_address,
                        ),
                        pc.button(
                            "Add",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.whatsapp
                            ),
                        ),
                    ),
                    pc.text(AddressesDashboardState.whatsapp_address_reset_message),
                ),
            ),
            pc.cond(
                AddressesDashboardState.has_no_sms_address,
                pc.vstack(
                    pc.hstack(
                        pc.text("SMS Address:"),
                        pc.input(
                            placeholder="Enter your SMS number...",
                            on_change=AddressesDashboardState.set_new_sms_address,
                        ),
                        pc.button(
                            "Add",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.sms
                            ),
                        ),
                    ),
                    pc.text(AddressesDashboardState.sms_address_reset_message),
                ),
            ),
            pc.cond(
                AddressesDashboardState.has_no_phone_address,
                pc.vstack(
                    pc.hstack(
                        pc.text("Phone Number:"),
                        pc.input(
                            placeholder="Enter your phone number...",
                            on_change=AddressesDashboardState.set_new_phone_address,
                        ),
                        pc.button(
                            "Add",
                            on_click=lambda _: AddressesDashboardState.change_address(
                                config.ADDRESSES_KEYS.phone
                            ),
                        ),
                    ),
                    pc.text(AddressesDashboardState.phone_address_reset_message),
                ),
            ),
            border_radius="15px",
            padding=5,
            border_color="black",
            border_width="thick",
        ),
    )


def addresses_presentation() -> pc.Component:
    """Generate addresses presentation for the user dashboard page.

    Returns:
        pc.Component: The addresses view component.
    """
    return pc.vstack(
        pc.text("Addresses:", as_="b"),
        pc.cond(
            AddressesDashboardState.has_addresses,
            user_addresses_view(),
            pc.text(
                "You are not registered at any address. Update your details here below."
            ),
        ),
        pc.cond(
            AddressesDashboardState.is_some_address_missing,
            available_addresses_view(),
        ),
    )
