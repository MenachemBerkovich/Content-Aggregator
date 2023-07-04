from typing import List, Dict, Set
from contextlib import suppress

import pynecone as pc

from contentaggregator.lib import config
from contentaggregator.lib.user.userauthentications import userentrancecontrol
from contentaggregator.lib.user import userinterface
from contentaggregator.lib.feeds import feed
from contentaggregator.lib.sqlmanagement import databaseapi


def prepare_specific_feed_details(feed_obj: feed.Feed) -> List[str | int]:
    return [
        feed_obj.image or "https://pynecone.io/black.png",
        feed_obj.title,
        feed_obj.description or feed_obj.title,
        feed_obj.id,
    ]


def prepare_user_feeds_details(
    user: userinterface.User,
) -> List[List[str | int]]:
    if check_feeds_existence(user):
        return [prepare_specific_feed_details(feed) for feed in user.feeds.collection]
    return []


def prepare_user_available_feeds(user: userinterface.User) -> List[List[str | int]]:
    suggested_feeds_data = databaseapi.get_feeds_set()
    suggested_feeds = [feed.FeedFactory.create(feed_data[0], feed_data[1]) for feed_data in suggested_feeds_data] 
    if user:
        return (
            [
                prepare_specific_feed_details(feed)
                for feed in suggested_feeds
                if feed not in user.feeds.collection
            ]
            if check_feeds_existence(user)
            else [prepare_specific_feed_details(feed) for feed in suggested_feeds]
        )


def check_feeds_existence(user: userinterface.User) -> bool:
    try:
        bool_value = bool(user.feeds)
    except Exception:
        bool_value = False
    return bool_value


class EntranceState(pc.State):
    """Manage user entrance process."""

    _user: userinterface.User | None = None
    username: str = ""
    password: str = ""
    message: str = ""
    is_clicked: bool = False
    #
    user_feeds_status: Dict[int, bool] = dict()
    available_feeds_status: Dict[int, bool] = dict()
    has_feeds: bool = False
    user_feeds: List[List[str | int]] = []
    available_feeds: List[List[str | int]] = []
    #
    has_addresses: bool = False
    email_address: str = ""
    whatsapp_address: str = ""
    phone_address: str = ""
    sms_address: str = ""
    is_authenticated: bool = False
    #
    send_timing: str = ""
    send_hour: str = ""


    def reload(self) -> None:
        """Needed for '/signin' or '/login' page on_load attrs."""
        self._user = None
        self.username = ""
        self.password = ""
        self.is_clicked = False
        self.message = ""
        self.is_authenticated = False

    def initialize_user_feeds(self) -> None:
        print("i am initializing")
        self.user_feeds = prepare_user_feeds_details(self._user)
        self.available_feeds = prepare_user_available_feeds(self._user)
        self.has_feeds = check_feeds_existence(self._user)
        self.has_addresses = bool(self._user.addresses)
        print(self.user_feeds, self.available_feeds)
        for feed_details in self.user_feeds:
            self.user_feeds_status[feed_details[3]] = True
            self.available_feeds_status[feed_details[3]] = False
        for feed_details in self.available_feeds:
            self.available_feeds_status[feed_details[3]] = True
            self.user_feeds_status[feed_details[3]] = False



    def initialize_user_addresses(self) -> None:
        if self.has_addresses:
            email_address_obj = self._user.addresses.collection.get(
                config.ADDRESSES_KEYS.email, None
            )
            self.email_address = email_address_obj.address if email_address_obj else ""
            whatsapp_address_obj = self._user.addresses.collection.get(
                config.ADDRESSES_KEYS.whatsapp, None
            )
            self.whatsapp_address = (
                whatsapp_address_obj.address if whatsapp_address_obj else ""
            )
            sms_address_obj = self._user.addresses.collection.get(
                config.ADDRESSES_KEYS.sms, None
            )
            self.sms_address = sms_address_obj.address if sms_address_obj else ""
            phone_address_obj = self._user.addresses.collection.get(
                config.ADDRESSES_KEYS.phone, None
            )
            self.phone_address = (
                phone_address_obj.address if phone_address_obj else ""
            )
            
    def initialize_user_sending_time(self) -> None:
        if self._user:
            if self._user.sending_time:
                self.send_timing = self._user.sending_time.sending_time.strftime("%H:%M")
                self.send_hour = self._user.sending_time.sending_schedule.name.capitalize()

    def log_in(self) -> pc.event.EventSpec | None:
        """Log in the current user.
        And redirect into the dashboard view page (if the login was successful).
        """
        self.is_clicked = True
        self.message = ""
        try:
            self._user = userentrancecontrol.log_in(self.username, self.password)
            self.initialize_user_feeds()
            self.initialize_user_addresses()
            self.initialize_user_sending_time()
            self.is_authenticated = True
            self.message = "Login successful!"
            return pc.redirect("/dashboard")
        except Exception as e:
            self.message = str(e)

    def sign_up(self) -> pc.event.EventSpec | None:
        """Sign up for new users."""
        self.is_clicked = True
        self.message = ""
        try:
            self._user = userentrancecontrol.sign_up(self.username, self.password)
            self.is_authenticated = True
            self.message = """Sign Up Success! Please white until user dashboard will be available,
                            #   and set your favorite feeds, addresses and sending time."""
            return pc.redirect("/dashboard")
        except Exception as e:
            self.message = str(e)


def entrance_message() -> pc.Component:
    """Generates conditional component message, accordance the backend occurrence.

    Returns:
        pc.Component: The conditional component message.
    """
    return pc.cond(EntranceState.is_clicked, pc.text(EntranceState.message, as_="b"))


def log_in_session() -> pc.Component:
    """Generates the login session page.

    Returns:
        pc.Component: the login session page.
    """
    return pc.vstack(
        pc.input(
            placeholder="Your username...",
            on_blur=EntranceState.set_username,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.input(
            placeholder="Your password...",
            type_="password",
            on_blur=EntranceState.set_password,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.button(
            "Login",
            on_click=EntranceState.log_in,
            bg="grey",
            color="white",
            margin_top=0,
            size="md",
            _hover={
                "box_shadow": "0 0 .12em .07em #EE756A, 0 0 .25em .11em #756AEE",
            },
        ),
        entrance_message(),
        justify="center",
        should_wrap_children=True,
        spacing="1em",
    )


def sign_up_session() -> pc.Component:
    """Generates a sign up session page.

    Returns:
        pc.Component: the sign up session page.
    """
    return pc.vstack(
        pc.input(
            placeholder="Choose your username...",
            on_blur=EntranceState.set_username,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.input(
            placeholder="Choose your password...",
            type_="password",
            on_blur=EntranceState.set_password,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.button(
            "Sign Up",
            on_click=EntranceState.sign_up,
            bg="grey",
            color="white",
            margin_top=0,
            size="md",
            _hover={
                "box_shadow": "0 0 .12em .07em #EE756A, 0 0 .25em .11em #756AEE",
            },
        ),
        entrance_message(),
        justify="center",
        should_wrap_children=True,
        spacing="1em",
    )
