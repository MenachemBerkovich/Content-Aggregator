"""User's username management and presentation."""

import pynecone as pc

from . import entrance


class DashboardUsernameState(entrance.EntranceState):
    """Username reset management"""

    new_username: str = ""
    username_reset_message: str = ""

    @pc.var
    def updated_username(self) -> str:
        """ComputedVar that return current username

        Returns:
            str: The current username.
        """
        if self._user:
            return self._user.username

    def save_new_username(self) -> None:
        """Save new username of the self._user
        """
        if self._user:
            try:
                self._user.username = self.new_username
                self.username_reset_message = "Saved Successfully:)"
            except Exception as e:
                self.username_reset_message = str(e)


def username_presentation() -> pc.Component:
    """Generate a username reset box part on the dashboard page.

    Returns:
        pc.Component: The component that will be displayed on the dashboard for username reset.
    """
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
