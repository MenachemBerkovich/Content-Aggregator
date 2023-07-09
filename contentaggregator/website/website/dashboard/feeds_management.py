"""User's feeds management and presentation.
"""

from typing import Dict, List

import pynecone as pc

from contentaggregator.lib.feeds import feed
from contentaggregator.lib.user.userproperties import collections
from . import entrance


class FeedsDashboardState(entrance.EntranceState):
    """A user feeds dashboard manager"""

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
    def is_available_feeds_exists(self) -> bool:
        """A ComputedVar that indicates if there are any feeds that the current self._user,
        does not subscribe to them.

        Returns:
            bool: True if there are, False otherwise.
        """
        return bool(self.available_feeds)

    def set_current_feed_id(self, feed_id: int) -> None:
        """Set the current_feed_id the user is currently engaged with.

        Args:
            feed_id (int): The feed id.
        """
        self.current_feed_id = feed_id

    def update_candidates_to_delete(self, is_selected: bool) -> None:
        """Update self._candidates_to_delete dictionary, with the user's selection or de-selection.

        Args:
            is_selected (bool): Has the user selected the feed or de-selected itץ
        """
        if is_selected:
            self._candidates_to_delete[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
            self.is_deletion_disabled = False
        else:
            self._candidates_to_delete.pop(self.current_feed_id)
            if not bool(self._candidates_to_delete):
                self.is_deletion_disabled = True

    def update_feeds_subscriptions(self) -> None:
        """Update self.user_feeds and self.available_feeds lists.
        Used after feed deletion, to update lists accordance the last changes.
        """
        for feed_obj in self._candidates_to_delete.values():
            self.user_feeds.remove(entrance.prepare_specific_feed_details(feed_obj))
            self.available_feeds.append(
                entrance.prepare_specific_feed_details(feed_obj)
            )
            self.available_feeds_status[feed_obj.id] = True
            self.user_feeds_status[feed_obj.id] = False

    def delete_feeds(self) -> None:
        """Delete all chosen feeds."""
        if self._user:
            try:
                self._user.feeds -= collections.UserSetController(
                    *tuple(self._candidates_to_delete.values())
                )
                self.update_feeds_subscriptions()
                self._candidates_to_delete.clear()
                if not self._user.feeds:
                    self.has_feeds = False
                self.is_deletion_disabled = True
                self.feeds_reset_add_message = ""
                self.feeds_reset_delete_message = (
                    "Feeds deleted successfully! please refresh to continue..."
                )
            except Exception as e:
                self.feeds_reset_delete_message = str(e)

    def update_candidates_to_add(self, is_selected: bool) -> None:
        """Update self._candidates_to_add dictionary,
        with the user's selection or de-selection.

        Args:
            is_selected (bool): Has the user selected the feed or de-selected it.
        """
        if is_selected:
            self._candidates_to_add[self.current_feed_id] = feed.FeedFactory.create(
                self.current_feed_id
            )
            self.is_addition_disabled = False
        else:
            self._candidates_to_add.pop(self.current_feed_id)
            if not bool(self._candidates_to_add):
                self.is_addition_disabled = True

    def update_feeds_availability(self) -> None:
        """Update self.user_feeds and self.available_feeds lists.
        Used after feed addition, to update lists accordance the last changes.
        """
        for feed_obj in self._candidates_to_add.values():
            self.available_feeds.remove(
                entrance.prepare_specific_feed_details(feed_obj)
            )
            self.user_feeds.append(entrance.prepare_specific_feed_details(feed_obj))
            self.user_feeds_status[feed_obj.id] = True
            self.available_feeds_status[feed_obj.id] = False

    def add_feeds(self) -> None:
        """Add all chosen feeds."""
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
                self.update_feeds_availability()
                self._candidates_to_add.clear()
                self.has_feeds = True
                self.is_addition_disabled = True
                self.feeds_reset_delete_message = ""
                self.feeds_reset_add_message = (
                    "Feeds added successfully! please refresh to continue..."
                )
            except Exception as e:
                self.feeds_reset_add_message = str(e)


def render_feed_box(
    feed_details: List[str],
    condition: pc.vars.BaseVar,
    is_candidate_to_delete: bool,
) -> pc.Component:
    """Render feed component with feed details.

    Args:
        feed_details (List[str]): A list that contains any data needed for rendering.
        condition (pc.vars.Var): The condition for feed component.
        is_candidate_to_delete (bool): If is a user's feed or not.

    Returns:
        pc.Component: The conditional component for specific feed.
    """
    _feed_title = feed_details[2]
    _feed_id = feed_details[3]
    _feed_website = FeedsDashboardState.websites_links[_feed_id]
    button_event_handler = (
        FeedsDashboardState.update_candidates_to_delete
        if is_candidate_to_delete
        else FeedsDashboardState.update_candidates_to_add
    )
    return pc.cond(
        condition,
        pc.hstack(
            pc.link(
                _feed_title,
                href=_feed_website,
                is_external=True,
            ),
            pc.checkbox(color_scheme="green", on_change=button_event_handler),
            on_mouse_over=lambda _: FeedsDashboardState.set_current_feed_id(_feed_id),
        ),
    )


def feeds_presentation() -> pc.Component:
    """Prepare the presentation of the feeds part on the dashboard.

    Returns:
        pc.Component: The component of the feed presentation.
    """
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
            FeedsDashboardState.is_available_feeds_exists,
            pc.vstack(
                pc.foreach(
                    FeedsDashboardState.available_feeds,
                    lambda feed_data: render_feed_box(
                        feed_data,
                        FeedsDashboardState.available_feeds_status[feed_data[3]],
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
