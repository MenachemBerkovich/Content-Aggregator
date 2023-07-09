"""Entrance module for users entrance management and presentation
"""
from typing import List, Dict

import pynecone as pc

from contentaggregator.lib import config
from contentaggregator.lib.user.userauthentications import userentrancecontrol
from contentaggregator.lib.user import userinterface
from contentaggregator.lib.feeds import feed
from contentaggregator.lib.sqlmanagement import databaseapi


def prepare_specific_feed_details(feed_obj: feed.Feed) -> List[str | int]:
    """Prepare specific feed details, in a json serializable form
    - List of the details needed to be presented on the dashboard page.

    Args:
        feed_obj (feed.Feed): The Feed object to extract details from.

    Returns:
        List[str | int]: List with the following details: feed.image, feed.title, feed.description, feed.id.
    """
    return [
        feed_obj.image or "https://pynecone.io/black.png",
        feed_obj.title,
        feed_obj.description or feed_obj.title,
        feed_obj.id,
    ]


def check_feeds_existence(user: userinterface.User) -> bool:
    """Checks whether `user` is registered at some feeds.

    Args:
        user (userinterface.User): The user to check.

    Returns:
        bool: True if user is registered at some feeds, False otherwise.
    """
    try:
        bool_value = bool(user.feeds)
    except Exception:
        bool_value = False
    return bool_value


class EntranceState(pc.State):
    """User entrance process manager."""

    # User backend var. There will be a real user object, lives at this state,
    # once login or sign-up is successful.
    _user: userinterface.User | None = None
    username: str = ""
    password: str = ""
    is_authenticated: bool = False  # ? it's still needed if we checking by self._user
    # Message to present on the entrance page when the user trying to login or sign up.
    message: str = ""
    is_clicked: bool = False
    #
    # For the FeedsDashboardState inheriting class.
    user_feeds_status: Dict[int, bool] = dict()  # ? still needed?
    available_feeds_status: Dict[int, bool] = dict()  # ? still needed?
    websites_links: Dict[int, str] = dict()
    has_feeds: bool = False
    # List of feed details where the user is registered.
    user_feeds: List[List[str | int]] = []
    # List of feed details where the user is unregistered.
    available_feeds: List[List[str | int]] = []
    #
    # For the AddressesDashboardState inheriting class.
    has_addresses: bool = False
    email_address: str = ""
    whatsapp_address: str = ""
    phone_address: str = ""
    sms_address: str = ""
    #
    # For the SendingTimeDashboard inheriting class.
    send_timing: str = ""
    send_hour: str = ""

    def reload(self) -> None:
        """Resets the entrance page components when it's reloaded."""
        self._user = None
        self.username = ""
        self.password = ""
        self.is_clicked = False
        self.message = ""
        self.is_authenticated = False

    def prepare_feed_lists(self) -> None:
        suggested_feeds_data = databaseapi.get_feeds_set()
        suggested_feeds = [
            feed.FeedFactory.create(feed_data[0], feed_data[1])
            for feed_data in suggested_feeds_data
        ]
        self.websites_links = {feed.id: feed.website for feed in suggested_feeds}
        if self._user:
            if self._user.feeds:
                self.available_feeds = [
                    prepare_specific_feed_details(feed)
                    for feed in suggested_feeds
                    if feed not in self._user.feeds.collection
                ]
                self.user_feeds = [
                    prepare_specific_feed_details(feed)
                    for feed in self._user.feeds.collection
                ]
            else:
                self.available_feeds = [
                    prepare_specific_feed_details(feed) for feed in suggested_feeds
                ]

    def initialize_user_feeds(self) -> None:
        """Initialize the user feeds list.
        Used for dashboard view.
        """
        self.prepare_feed_lists()
        self.has_feeds = check_feeds_existence(self._user)
        self.has_addresses = bool(self._user.addresses)
        print(self.user_feeds, self.available_feeds)
        for (
            feed_details
        ) in (
            self.user_feeds
        ):  # ? from this line on... it's neede if the dictionories doesn't helpful
            self.user_feeds_status[feed_details[3]] = True  # ?
            self.available_feeds_status[feed_details[3]] = False  # ?
        for feed_details in self.available_feeds:  # ?
            self.available_feeds_status[feed_details[3]] = True  # ?
            self.user_feeds_status[feed_details[3]] = False  # ?

    def initialize_user_addresses(self) -> None:
        """Initialize user addresses,
        so that they will be available for display in the input boxes by default.
        """
        if self.has_addresses:
            for address_key, address in self._user.addresses.collection.items():
                self.__dict__[f"{address_key}_address"] = address.address

    def initialize_user_sending_time(self) -> None:
        """Initialize user sending time preference."""
        if self._user and self._user.sending_time:
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
            self.is_authenticated = True  # ?
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
            self.is_authenticated = True  # ?
            self.message = """Sign Up Success! Please white until user dashboard will be available \nand set your favorite feeds, addresses and sending time."""
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
        pc.Component: the login session page component.
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
