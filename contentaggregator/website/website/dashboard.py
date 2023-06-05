from typing import List, Set, Any

import pynecone as pc

from contentaggregator.lib.user.userproperties import collections
from contentaggregator.lib.user.userauthentications import pwdhandler
from contentaggregator.lib.feeds import feed
from . import entrance


class DashboardUsernameState(entrance.EntranceState):
    new_username: str = ""
    username_reset_message: str = ""
    # @pc.var
    # def encrypted_password(self) -> str:
    #     if self.is_authenticated:
    #         return entrance.CURRENT_USER.password

    @pc.var
    def updated_username(self) -> str:
        if self.is_authenticated:
            return entrance.CURRENT_USER.username

    def save_new_username(self) -> None:
        if self.is_authenticated:
            try:
                entrance.CURRENT_USER.username = self.new_username
                self.username_reset_message = "Saved Successfully:)"
            except Exception as e:
                self.username_reset_message = str(e)


def username_presentation() -> pc.Component:
    return pc.vstack(
        pc.text("User name:", as_="b"),
        pc.hstack(
            pc.input(
                place_holder="New username",
                default_value=DashboardUsernameState.updated_username,
                on_change=DashboardUsernameState.set_new_username,
            ),
            pc.button(
                "Change",
                on_click=DashboardUsernameState.save_new_username,
            ),
        ),
        pc.text(DashboardUsernameState.username_reset_message),
    )


class DashboardPasswordState(entrance.EntranceState):
    old_password: str = ""
    new_password: str = ""
    new_password_confirmation: str = ""
    password_reset_message: str = ""

    def save_new_password(self) -> None:
        if not self.is_authenticated:
            return
        if not pwdhandler.is_same_password(
            self.old_password, entrance.CURRENT_USER.password
        ):
            self.password_reset_message = "Old password is incorrect"
        elif self.new_password != self.new_password_confirmation:
            self.password_reset_message = "New password has not been confirmed"
        elif self.old_password != self.new_password:
            try:
                entrance.CURRENT_USER.password = self.new_password
                self.password_reset_message = "Password changed successfully!"
                self.old_password = ""
                self.new_password = ""
                self.new_password_confirmation = ""
            except Exception as e:
                self.password_reset_message = str(e)


def password_presentation() -> pc.Component:
    return pc.box(
        pc.vstack(
            pc.text("Password:", as_="b"),
            pc.input(
                value=DashboardPasswordState.old_password,
                placeholder="Old Password",
                on_change=DashboardPasswordState.set_old_password,
            ),
            pc.input(
                value=DashboardPasswordState.new_password,
                placeholder="New Password",
                on_change=DashboardPasswordState.set_new_password,
            ),
            pc.input(
                value=DashboardPasswordState.new_password_confirmation,
                placeholder="Confirm New Password",
                on_change=DashboardPasswordState.set_new_password_confirmation,
            ),
            pc.button("Change", on_click=DashboardPasswordState.save_new_password),
        ),
        pc.text(DashboardPasswordState.password_reset_message, as_="b"),
    )


class FeedsDashboardState(entrance.EntranceState):
    # feed_selected: bool = False
    # _user_feeds = (
    #     "None" if not entrance.CURRENT_USER else entrance.CURRENT_USER.feeds.collection
    # )
    _selected_feeds: Set[feed.Feed] = set()
    feeds_reset_message: str = ""

    def delete_feeds(self) -> None:
        if self.is_authenticated:
            entrance.CURRENT_USER.feeds -= collections.UserSetController(
                *self._selected_feeds
            )
            self._selected_feeds.clear()

    def update_feed(self, feed_id: int) -> None:
        if feed not in self._selected_feeds:
            self._selected_feeds.add(feed)
        else:
            self._selected_feeds.remove(feed)

    # def render_feed_box(self, feed: feed.Feed) -> pc.Component:
    #     return pc.hstack(
    #         pc.link(
    #             pc.image(src=feed.image or "https://pynecone.io/black.png"),
    #             href=feed.website,
    #         ),
    #         pc.text(feed.title),
    #         pc.checkbox(
    #             "Select",
    #             color_scheme="green",
    #             on_change=lambda: FeedsDashboardState().update_feed(feed),
    #         ),
    #     )

    @pc.var
    def has_feeds(self) -> bool:
        try:
            bool_value = bool(entrance.CURRENT_USER.feeds)
            if not bool_value:
                self.feeds_reset_message = "Currently don't you have any feeds:( you can change it here below:)"
        except Exception:
            bool_value = False
        return bool_value

    @pc.var
    def user_feeds(self) -> List[List[str]]:
        if self.has_feeds:
            return [
                [
                    feed.image or "https://pynecone.io/black.png",
                    feed.title,
                    feed.description or feed.title,
                    feed.id,
                ]
                for feed in entrance.CURRENT_USER.feeds.collection
            ]

    # def render_feeds(self) -> pc.Component:
    #     if entrance.EntranceState.is_authenticated:
    #         return pc.vstack(
    #             pc.text("Feeds:"),
    #             pc.foreach(entrance.CURRENT_USER.feeds.collection, render_feed_box),
    #             pc.button(use
    #                 "Delete",
    #                 is_disabled=FeedsDashboardState.is_deletion_disabled,
    #                 on_click=FeedsDashboardState.delete_feeds,
    #             ),
    #         )
    #     else:
    #         pc.text("Login")

    # @pc.var
    # def feeds_boxes(self) -> pc.Component:
    #     if self.is_authenticated:
    #         return (
    #             pc.foreach(list(entrance.CURRENT_USER.feeds.collection), render_feed_box),
    #         )
    #     return pc.text("login")

    @pc.var
    def is_deletion_disabled(self) -> bool:
        return bool(self._selected_feeds)


# def render_row(feed: feed.Feed) -> pc.Component:
#     if entrance.EntranceState.is_authenticated:
#         return pc.tr(
#             pc.td(
#                 pc.link(
#                     pc.image(src=feed.image or "https://pynecone.io/black.png"),
#                     href=feed.website,
#                 ),
#                 pc.text(feed.title),
#             ),
#             pc.td(pc.text(feed.description)),
#             pc.td(pc.text(feed.rating)),
#             pc.td(
#                 pc.button(
#                     "Delete",
#                     on_click=FeedsDashboardState.delete_feed,
#                     # on_mouse_over=FeedsDashboardState.set_selected_feed_id,
#                 )
#             ),
#         )


def render_feed_box(feed_details: List[str]) -> pc.Component:
    return pc.hstack(
        pc.link(
            pc.image(src=feed_details[0] or "https://pynecone.io/black.png"),
            href=feed_details[1],
        ),
        pc.text(feed_details[2]),
        pc.checkbox(
            "Select",
            color_scheme="green",
            # on_change=lambda feed_details: FeedsDashboardState().update_feed(
            # feed_details[3]
        ),
    )
    # )


def feeds_presentation() -> pc.Component:
    return pc.vstack(
        pc.text("Feeds:"),
        pc.cond(
            FeedsDashboardState.has_feeds,
            pc.vstack(
                pc.foreach(FeedsDashboardState.user_feeds, render_feed_box),
                pc.button(
                    "Delete",
                    is_disabled=FeedsDashboardState.is_deletion_disabled,
                    on_click=FeedsDashboardState.delete_feeds,
                ),
            ),
        ),
        pc.text(FeedsDashboardState.feeds_reset_message),
    )
    #     pc.table(
    #         pc.thead(
    #             pc.tr(
    #                 pc.foreach(
    #                     FeedsDashboardState.columns, lambda header: pc.th(header)
    #                 )
    #             )
    #         ),
    #         pc.tbody(
    #             pc.foreach(
    #                 FeedsDashboardState.user_feeds_set,
    #                 lambda feed: render_row(feed),
    #             )
    #         ),
    #     ),


def addresses_presentation() -> pc.Component:
    return pc.text("addresses")


def sending_time_presentation() -> pc.Component:
    return pc.text("sending_time")


def landing() -> pc.Component:
    return pc.cond(
        entrance.EntranceState.is_authenticated,
        pc.vstack(
            username_presentation(),
            password_presentation(),
            feeds_presentation(),
            addresses_presentation(),
            sending_time_presentation(),
        ),
        pc.hstack(
            pc.text("403:( You need"),
            pc.link("login", href="/login", as_="b"),
            pc.text(" or "),
            pc.link("sign up", href="/signup", as_="b"),
        ),
    )


class DashboardState(entrance.EntranceState):
    def reload_dashboard(self) -> None:
        # reload username state
        DashboardUsernameState.new_username = ""
        DashboardUsernameState.username_reset_message = ""
        # reload password state
        DashboardPasswordState.old_password = ""
        DashboardPasswordState.new_password = ""
        DashboardPasswordState.new_password_confirmation = ""
        DashboardPasswordState.password_reset_message = ""
