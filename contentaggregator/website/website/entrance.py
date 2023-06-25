from typing import List

import pynecone as pc

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
) -> List[List[str | int]] | None:
    if check_feeds_existence(user):
        return [prepare_specific_feed_details(feed) for feed in user.feeds.collection]


def prepare_user_available_feeds(user: userinterface.User) -> List[List[str | int]]:
    suggested_feeds = databaseapi.get_feeds_set()
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
    # is_authenticated: bool = False
    user_feeds: List[List[str | int]] | None = None
    available_feeds: List[List[str | int]] | None = None
    has_feeds: bool = False

    @pc.var    
    def is_authenticated(self) -> bool:
        return bool(self._user)
    
    def reload(self) -> None:
        """Needed for '/signin' or '/login' page on_load attrs."""
        self._user = None
        self.username = ""
        self.password = ""
        # Describe state like is not clicked.
        self.is_clicked = False
        # Determine message to be nothing.
        self.message = ""
        #self.is_authenticated = False

    def log_in(self) -> pc.event.EventSpec | None:
        """Log in the current user.
        And redirect into the dashboard view page (if the login was successful).
        """
        self.is_clicked = True
        self.message = ""
        try:
            self._user = userentrancecontrol.log_in(
                self.username, self.password
            )
            self.message = "Login successful!"
            self.user_feeds = prepare_user_feeds_details(self._user)
            self.available_feeds = prepare_user_available_feeds(self._user)
            self.has_feeds = check_feeds_existence(self._user)
            # self.is_authenticated = True
            return pc.redirect("/dashboard")
        except Exception as e:
            self.message = str(e)

    def sign_up(self) -> pc.event.EventSpec | None:
        """Sign up for new users."""
        self.is_clicked = True
        self.message = ""
        try:
            self._user = userentrancecontrol.sign_up(
                self.username, self.password
            )
            #self.is_authenticated = True
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


# class DashboardState(EntranceState):
#     @pc.var
#     def username(self) -> str:
#         return CURRENT_USER.username if CURRENT_USER else ""


# def username_presentation() -> pc.Component:
#     return pc.hstack(pc.text("User name:", as_="b"), pc.text(DashboardState.username))


# def password_presentation() -> pc.Component:
#     return pc.text("password")


# def feeds_presentation() -> pc.Component:
#     return pc.text("feeds")


# def addresses_presentation() -> pc.Component:
#     return pc.text("addresses")


# def sending_time_presentation() -> pc.Component:
#     return pc.text("sending_time")


# def landing() -> pc.Component:
#     return pc.vstack(
#         username_presentation(),
#         password_presentation(),
#         feeds_presentation(),
#         addresses_presentation(),
#         sending_time_presentation(),
#     )
