from typing import Dict, List

import pynecone as pc

from contentaggregator.lib.feeds import feed
from contentaggregator.lib.user.userproperties import collections
from . import entrance

feed_to_check: int = -1


class FeedsDashboardState(entrance.EntranceState):
    _candidates_to_delete: Dict[int, feed.Feed] = dict()
    _candidates_to_add: Dict[int, feed.Feed] = dict()
    feeds_reset_add_message: str = ""
    feed_to_check: int = -1
    current_feed_id: int = -1
    is_deletion_disabled: bool = True
    is_addition_disabled: bool = True
    feeds_reset_add_message: str = ""
    feeds_reset_delete_message: str = ""

    @pc.var
    def has_feeds(self) -> bool:
        try:
            bool_value = bool(self._user.feeds)
        except Exception:
            bool_value = False
        return bool_value

    @pc.var
    def is_available_feeds_exists(self) -> bool:
        print(self.available_feeds)
        return bool(self.available_feeds)

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
                    self.available_feeds_status[feed_obj.id] = True
                    self.user_feeds_status[feed_obj.id] = False
                self._candidates_to_delete.clear()
                if not self._user.feeds:
                    self.has_feeds = False
                self.is_deletion_disabled = True
                self.feeds_reset_add_message = ""
                self.feeds_reset_delete_message = (
                    "Feeds deleted successfully! please refresh to continue..."
                )
                self.initialize_user_feeds()
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
                    self.user_feeds.append(new_feed_details)
                    self.user_feeds_status[feed_obj.id] = True
                    self.available_feeds_status[feed_obj.id] = False
               # self.initialize_user_feeds()
                self._candidates_to_add.clear()
                self.has_feeds = True
                self.is_addition_disabled = True
                self.feeds_reset_delete_message = ""
                self.feeds_reset_add_message = (
                    "Feeds added successfully! please refresh to continue..."
                )
            except Exception as e:
                self.feeds_reset_add_message = str(e)

    @pc.var
    def has_specific_feed(self) -> bool:
        print(self.feed_to_check)
        return self.feed_to_check in self._candidates_to_delete

    @pc.var
    def has_no_specific_feed(self) -> bool:
        print(self.feed_to_check)
        return self.feed_to_check not in self._candidates_to_delete

    # @classmethod
    # @pc.var
    # def is_subscribed_to(cls, feed_id: int) -> bool:
    #     try:
    #         return feed_id in cls._user.feeds.collection
    #     except Exception:
    #         return False

    # @classmethod
    # @pc.var
    # def is_not_subscribed_to(cls, feed_id: int) -> bool:
    #     return not cls.is_subscribed_to(feed_id)
    @classmethod
    def is_feed_in_collection(
        cls, feed_details: List[str | int], collection: List[List[str | int]]
    ) -> bool:
        """_summary_

        Args:
            feed_details (List[str  |  int]): _description_
            collection (List[List[str  |  int]]): _description_

        Returns:
            bool: _description_
        """
        try:
            return feed_details[3] in cls._user.feeds.collection
        except Exception:
            return False

    @classmethod
    def is_feed_should_appear(
        cls, feed_details: List[str | int], is_candidate_to_delete: bool
    ) -> bool:
        return (
            feed_details not in cls.available_feeds
            if is_candidate_to_delete
            else feed_details not in cls.user_feeds
        )


def has_this_feed(feed_id: int) -> pc.vars.ComputedVar:
    FeedsDashboardState.feed_to_check = feed_id
    return FeedsDashboardState.has_specific_feed


def has_no_this_feed(feed_id: int) -> pc.vars.ComputedVar:
    FeedsDashboardState.feed_to_check = feed_id
    return FeedsDashboardState.has_no_specific_feed


def check_feed_existance(feed_id: int, user) -> bool:
    try:
        return feed_id in user.feeds
    except Exception:
        return False


def render_feed_box(
    feed_details: List[str],
    condition: pc.vars.Var,
    is_candidate_to_delete: bool,
) -> pc.Component:
    _feed_image = str(feed_details[0])
    _feed_website = str(feed_details[1])
    _feed_title = feed_details[2]
    _feed_id = feed_details[3]
    button_event_handler = (
        FeedsDashboardState.update_candidates_to_delete
        if is_candidate_to_delete
        else FeedsDashboardState.update_candidates_to_add
    )
    # condition = (
    #     lambda: FeedsDashboardState.user_feeds_status[_feed_id]
    #     if is_candidate_to_delete
    #     else lambda: FeedsDashboardState.available_feeds_status[_feed_id]
    # )
    # try:
    #     condition = _feed_id in FeedsDashboardState._user.feeds if is_candidate_to_delete else _feed_id not in FeedsDashboardState._user.feeds
    # except Exception:
    #     condition = False
    # if is_candidate_to_delete
    # else not FeedsDashboardState.is_feed_in_collection(
    #     feed_details,
    #     FeedsDashboardState.available_feeds
    # )
    # )
    return pc.cond(
        condition,
        pc.hstack(
            pc.link(
                _feed_title,
                href=_feed_website,
            ),
            pc.checkbox("Select", color_scheme="green", on_change=button_event_handler),
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
                    lambda feed_data: render_feed_box(
                        feed_data,
                        FeedsDashboardState.user_feeds_status[feed_data[3]],
                        True,
                    ),
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
            FeedsDashboardState.is_available_feeds_exists,
            pc.vstack(
                pc.foreach(
                    FeedsDashboardState.available_feeds,
                    lambda feed_data: render_feed_box(
                        feed_data,
                        FeedsDashboardState.available_feeds_status[feed_data[3]] == True,
                        False,
                    ),
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
            pc.text("No additional available feeds"),
        ),
        pc.text(FeedsDashboardState.feeds_reset_add_message),
    )
