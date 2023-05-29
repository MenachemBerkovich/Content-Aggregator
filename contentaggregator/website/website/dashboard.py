import pynecone as pc

from . import entrance


class DashboardState(entrance.EntranceState):
    pass
    # @pc.var
    # def username(self) -> str:
    #     return entrance.CURRENT_USER.username if entrance.CURRENT_USER else ""

    # @pc.var
    # def user_password(self) -> str:
    #      return entrance.EntranceState.password if entrance.CURRENT_USER else ""


def username_presentation() -> pc.Component:
    return pc.hstack(
        pc.text("User name:", as_="b"), pc.text(entrance.EntranceState.username)
    )


def password_presentation() -> pc.Component:
    return pc.hstack(
        pc.text("Password:", as_="b"), pc.text(entrance.EntranceState.password)
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
