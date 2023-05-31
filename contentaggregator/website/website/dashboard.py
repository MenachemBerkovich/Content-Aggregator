import pynecone as pc

from contentaggregator.lib.user.userauthentications import pwdhandler
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


def feeds_presentation() -> pc.Component:
    return pc.text("feeds")


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
