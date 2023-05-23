import pynecone as pc

from contentaggregator.lib.user.userauthentications import userentrancecontrol
from contentaggregator.lib.user.userinterface import User


class SingingState(pc.State):
    username: str = ""
    password: str = ""

    def sign_in(self):
        self.user = userentrancecontrol.log_in(self.username, self.password)
        # except Exception as e:

    def sign_up(self):
        self.user = userentrancecontrol.sign_up(self.username, self.password)


def sign_in_session() -> pc.Component:
    return pc.vstack(
        pc.input(
            placeholder="Your username...",
            on_blur=SingingState.set_username,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.input(
            placeholder="Your password...",
            on_blur=SingingState.set_password,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.button(
            "Sign In",
            on_click=SingingState.sign_in,
            bg="grey",
            color="white",
            margin_top=0,
            size="md",
            _hover={
                "box_shadow": "0 0 .12em .07em #EE756A, 0 0 .25em .11em #756AEE",
            },
        ),
        justify="center",
        should_wrap_children=True,
        spacing="1em",
    )

def sign_up_session() -> pc.Component:
    return pc.vstack(
        pc.input(
            placeholder="Choose your username...",
            on_blur=SingingState.set_username,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.input(
            placeholder="Choose your password...",
            on_blur=SingingState.set_password,
            color="#676767",
            type="username",
            size="md",
            border="2px solid #f4f4f4",
            box_shadow="rgba(0, 0, 0, 0.08) 0px 4px 12px",
            bg="rgba(255,255,255,.5)",
        ),
        pc.button(
            "Sign Up",
            on_click=SingingState.sign_up,
            bg="grey",
            color="white",
            margin_top=0,
            size="md",
            _hover={
                "box_shadow": "0 0 .12em .07em #EE756A, 0 0 .25em .11em #756AEE",
            },
        ),
        justify="center",
        should_wrap_children=True,
        spacing="1em",
    )