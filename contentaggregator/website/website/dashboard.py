# from __future__ import annotations
from typing import List, Set, Any, Dict

import pynecone as pc

from contentaggregator.lib.user.userproperties import collections
from contentaggregator.lib.user import userinterface
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
    _candidates_to_delete: Dict[int, feed.Feed] = dict()
    _candidates_to_add: Dict[int, feed.Feed] = dict()
    feeds_reset_add_message: str = ""
    current_feed_id: int = -1
    is_deletion_disabled: bool = True
    is_addition_disabled: bool = True
    feeds_reset_add_message: str = ""
    feeds_reset_delete_message: str = ""

    def set_current_feed_id(self, feed_id: int) -> None:
        self.current_feed_id = feed_id

    def update_candidates_to_delete(self, is_selected: bool) -> None:
        if is_selected:
            self._candidates_to_delete[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
            self.is_deletion_disabled = False
        else:
            self._candidates_to_delete.pop(self.current_feed_id)
            if not bool(self._candidates_to_delete):
                self.is_deletion_disabled = True

    def delete_feeds(self) -> None:
        if self._user:
            try:
                self._user.feeds -= collections.UserSetController(
                    *tuple(self._candidates_to_delete.values())
                )
                for feed_obj in self._candidates_to_delete.values():
                    self.user_feeds.remove(
                        entrance.prepare_specific_feed_details(feed_obj)
                    )
                    self.available_feeds.append(
                        entrance.prepare_specific_feed_details(feed_obj)
                    )
                self._candidates_to_delete.clear()
                if not self._user.feeds:
                    self.has_feeds = False
                self.is_deletion_disabled = True
                self.feeds_reset_delete_message = (
                    "Feeds deleted successfully! please refresh to continue..."
                )
            except Exception as e:
                self.feeds_reset_delete_message = str(e)

    def update_candidates_to_add(self, is_selected: bool) -> None:
        if is_selected:
            self._candidates_to_add[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
            self.is_addition_disabled = False
        else:
            self._candidates_to_add.pop(self.current_feed_id)
            if not bool(self._candidates_to_add):
                self.is_addition_disabled = True

    def add_feeds(self) -> None:
        if self._user:
            try:
                if self._user.feeds:
                    self._user.feeds += collections.UserSetController(
                        *tuple(self._candidates_to_add.values())
                    )
                else:
                    self._user.feeds = collections.UserSetController(
                        *tuple(self._candidates_to_add.values())
                    )
                for feed_obj in self._candidates_to_add.values():
                    self.available_feeds.remove(
                        entrance.prepare_specific_feed_details(feed_obj)
                    )
                    new_feed_details = entrance.prepare_specific_feed_details(feed_obj)
                    if bool(self.user_feeds):
                        self.user_feeds.append(new_feed_details)
                    else:
                        self.user_feeds = [new_feed_details]
                self._candidates_to_add.clear()
                self.has_feeds = True
                self.is_addition_disabled = True
                self.feeds_reset_add_message = (
                    "Feeds added successfully! please refresh to continue..."
                )
            except Exception as e:
                self.feeds_reset_add_message = str(e)

    @classmethod
    def is_feed_in_collection(
        self, feed_details: List[str | int], collection: List[List[str | int]]
    ) -> bool:
        return feed_details in collection


def render_feed_box(
    feed_details: List[str], is_candidate_to_delete: bool
) -> pc.Component:
    _feed_image = str(feed_details[0])
    _feed_website = str(feed_details[1])
    _feed_title = feed_details[2]
    _feed_id = feed_details[3]

    return pc.cond(
        FeedsDashboardState.is_feed_in_collection(
            feed_details, FeedsDashboardState.user_feeds
        )
        if is_candidate_to_delete
        else FeedsDashboardState.is_feed_in_collection(
            feed_details, FeedsDashboardState.available_feeds
        ),
        pc.hstack(
            pc.link(
                _feed_title,
                href=_feed_website,
            ),
            pc.checkbox(
                "Select",
                color_scheme="green",
                on_change=FeedsDashboardState.update_candidates_to_delete
                if is_candidate_to_delete
                else FeedsDashboardState.update_candidates_to_add,
            ),
            on_mouse_over=lambda _: FeedsDashboardState.set_current_feed_id(_feed_id),
        ),
    )


def feeds_presentation() -> pc.Component:
    return pc.vstack(
        pc.text("Feeds:", as_="b"),
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
                border_radius="15px",
                padding=5,
                border_color="black",
                border_width="thick",
            ),
            pc.text(
                "Currently, Don't you have any feeds... You can choose your favorite feeds below."
            ),
        ),
        pc.text(FeedsDashboardState.feeds_reset_delete_message),
        pc.text("Available feeds:", as_="b"),
        pc.cond(
            # entrance.EntranceState.is_authenticated,
            bool(FeedsDashboardState.available_feeds),
            pc.vstack(
                pc.foreach(
                    FeedsDashboardState.available_feeds,
                    lambda feed_data: render_feed_box(feed_data, False),
                ),
                pc.button(
                    "Add",
                    is_disabled=FeedsDashboardState.is_addition_disabled,
                    on_click=FeedsDashboardState.add_feeds,
                ),
                border_radius="15px",
                padding=5,
                border_color="black",
                border_width="thick",
            ),
            pc.text("No additional available feeds(:"),
        ),
        pc.text(FeedsDashboardState.feeds_reset_add_message),
    )


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
        FeedsDashboardState.feeds_reset_add_message = ""
        FeedsDashboardState.is_addition_disabled = True
        FeedsDashboardState.is_deletion_disabled = True
