"""User's passwords management and presentation.
"""
import pynecone as pc

from contentaggregator.lib.user.userauthentications import pwdhandler
from . import entrance


class DashboardPasswordState(entrance.EntranceState):
    """Password state manager"""

    old_password: str = ""
    new_password: str = ""
    new_password_confirmation: str = ""
    password_reset_message: str = ""

    def save_new_password(self) -> None:
        """Save new password for self._user"""
        if not self._user:
            return
        # Verify old password correctness and new password compatibility.
        if not pwdhandler.is_same_password(self.old_password, self._user.password):
            self.password_reset_message = "Old password is incorrect"
        elif self.new_password != self.new_password_confirmation:
            self.password_reset_message = "New password has not been confirmed"
        # If new password is not realy `new` - it's the same with the old: do nothing.
        # Else reset self._user.password
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
    """Generate a password reset box part an the dashboard page.

    Returns:
        pc.Component: The component that will be displayed on the dashboard for password reset.
    """
    return pc.box(
        pc.vstack(
            pc.text("Password:", as_="b"),
            pc.input(
                type_="password",
                value=DashboardPasswordState.old_password,
                placeholder="Old Password",
                on_change=DashboardPasswordState.set_old_password,
            ),
            pc.input(
                type_="password",
                value=DashboardPasswordState.new_password,
                placeholder="New Password",
                on_change=DashboardPasswordState.set_new_password,
            ),
            pc.input(
                type_="password",
                value=DashboardPasswordState.new_password_confirmation,
                placeholder="Confirm New Password",
                on_change=DashboardPasswordState.set_new_password_confirmation,
            ),
            pc.button("Change", on_click=DashboardPasswordState.save_new_password),
        ),
        pc.text(DashboardPasswordState.password_reset_message, as_="b"),
    )
