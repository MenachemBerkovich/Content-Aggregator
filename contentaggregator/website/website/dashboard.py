from typing import List, Set, Any, Dict

import pynecone as pc

from contentaggregator.lib.user.userproperties import collections
from contentaggregator.lib.user.userauthentications import pwdhandler
from contentaggregator.lib.feeds import feed
from contentaggregator.lib.sqlmanagement import databaseapi
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
        if self._user:
            return self._user.username

    def save_new_username(self) -> None:
        if self._user:
            try:
                self._user.username = self.new_username
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
        if not self._user:
            return
        if not pwdhandler.is_same_password(self.old_password, self._user.password):
            self.password_reset_message = "Old password is incorrect"
        elif self.new_password != self.new_password_confirmation:
            self.password_reset_message = "New password has not been confirmed"
        elif self.old_password != self.new_password:
            try:
                self._user.password = self.new_password
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
    _suggested_feeds: Set[feed.Feed] = databaseapi.get_feeds_set()
    _candidates_to_delete: Dict[int, feed.Feed] = dict()
    _candidates_to_add: Dict[int, feed.Feed] = dict()
    feeds_reset_delete_message: str = ""
    feeds_reset_add_message: str = ""
    current_feed_id: int = -1

    def set_current_feed_id(self, feed_id: int) -> None:
        self.current_feed_id = feed_id

    def set_feed_to_delete(self, is_selected: bool) -> None:
        print(is_selected)
        if (
            is_selected
        ):  # and self.current_feed_id not in [feed.id for feed in self._selected_feeds]:
            self._candidates_to_delete[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
        else:
            self._candidates_to_delete.pop(self.current_feed_id)

    def delete_feeds(self) -> None:
        if self._user:
            self._user.feeds -= collections.UserSetController(
                *tuple(self._candidates_to_delete.values())
            )
            self._candidates_to_delete.clear()

    def set_feed_to_add(self, is_selected: bool) -> None:
        print(is_selected, self.current_feed_id)
        if is_selected:
            self._candidates_to_add[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
        else:
            self._candidates_to_add.pop(self.current_feed_id)
        print(self._candidates_to_add)

    def add_feeds(self) -> None:
        if self._user:
            if self._user.feeds:
                print(f"User feeds are: {self._user.feeds}")
                self._user.feeds += collections.UserSetController(
                    *tuple(self._candidates_to_add.values())
                )
            else:
                self._user.feeds = collections.UserSetController(
                    *tuple(self._candidates_to_add.values())
                )
            print(self._candidates_to_add)
            self._candidates_to_add.clear()

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
            bool_value = bool(self._user.feeds)
            if not bool_value:
                self.feeds_reset_delete_message = "Currently don't you have any feeds:( you can change it here below:)"
        except Exception:
            bool_value = False
        return bool_value

    @pc.var
    def user_feeds(self) -> List[List[str | int]]:
        if self.has_feeds:
            return [
                [
                    feed.image or "https://pynecone.io/black.png",
                    feed.title,
                    feed.description or feed.title,
                    feed.id,
                ]
                for feed in self._user.feeds.collection
            ]

    @pc.var
    def available_feeds(self) -> List[List[str | int]]:
        if self._user:
            return (
                [
                    [
                        feed.image or "https://pynecone.io/black.png",
                        feed.website,
                        feed.title,
                        feed.description or feed.title,
                        feed.id,
                    ]
                    for feed in self._suggested_feeds
                    if feed not in self._user.feeds.collection
                ]
                if self._user.feeds
                else [
                    [
                        feed.image or "https://pynecone.io/black.png",
                        feed.website,
                        feed.title,
                        feed.description or feed.title,
                        feed.id,
                    ]
                    for feed in self._suggested_feeds
                ]
            )

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
        return not bool(self._candidates_to_delete)

    @pc.var
    def is_add_disabled(self) -> bool:
        return not bool(self._candidates_to_add)


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


def render_feed_box(
    feed_details: List[str | int], is_candidate_to_delete: bool
) -> pc.Component:
    print(feed_details)
    _feed_image = str(feed_details[0])
    _feed_website = str(feed_details[1])
    _feed_title = feed_details[2]

    print(feed_details)
    return pc.hstack(
        pc.link(
            _feed_title,
            href=_feed_website,
        ),
        # pc.link(feed_details[2], href=feed_details[1]),
        pc.checkbox(
            "Select",
            color_scheme="green",
            on_change=FeedsDashboardState.set_feed_to_delete
            if is_candidate_to_delete
            else FeedsDashboardState.set_feed_to_add,
        ),
        on_mouse_over=lambda _: FeedsDashboardState.set_current_feed_id(
            feed_details[4]
        ),
    )


def feeds_presentation() -> pc.Component:
    return pc.vstack(
        pc.text("Feeds:"),
        pc.cond(
            FeedsDashboardState.has_feeds,
            pc.vstack(
                pc.foreach(
                    FeedsDashboardState.user_feeds,
                    lambda feed_data: render_feed_box(feed_data, True),
                ),
                pc.button(
                    "Delete",
                    is_disabled=FeedsDashboardState.is_deletion_disabled,
                    on_click=FeedsDashboardState.delete_feeds,
                ),
            ),
        ),
        pc.text(FeedsDashboardState.feeds_reset_delete_message),
        pc.foreach(
            FeedsDashboardState.available_feeds,
            lambda feed_data: render_feed_box(feed_data, False),
        ),
        pc.button(
            "Add",
            is_disabled=FeedsDashboardState.is_add_disabled,
            on_click=FeedsDashboardState.add_feeds,
        ),
        pc.text(FeedsDashboardState.feeds_reset_add_message),
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
            pc.link(f"sign up", href="/signup", as_="b"),
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
        # reload feeds state
        FeedsDashboardState.feeds_reset_delete_message = ""
