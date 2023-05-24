""""""
import pynecone as pc

from . import entrance


def index() -> pc.Component:
    return pc.vstack(
        pc.text(
            "Welcome to Bermen!",
            font_size="4em",
            font_weight=700,
            font_family="Inter",
        ),
        pc.text(
            "Here for you day and night...",
            font_size="4em",
            font_weight=800,
            font_family="Inter",
            background_image="linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)",
            background_clip="text",
        ),
        pc.vstack(
            pc.text(
                "All your interests in one place!",
                font_size="2em",
                font_weight=800,
            ),
            pc.container(
                pc.text(
                    """
                As a barmen, I constantly collect content for you from various sources,
                prepare it in the most beautiful way, and serve you cold and refreshing...
                """,
                    font_size="2em",
                    font_weight=800,
                    color="grey",
                ),
                pc.text(
                    "Get your customized content - from anywhere to one place:",
                    font_size="2em",
                    font_weight=800,
                ),
                pc.center(
                    pc.list(
                        pc.list_item(
                            *(
                                pc.hstack(
                                    pc.icon(tag="check_circle", color="green"),
                                    pc.text(
                                        service,
                                        margin_left="0.5em",
                                        font_size="1em",
                                        font_weight=800,
                                    ),
                                )
                                for service in [
                                    "Email",
                                    "WhatsApp",
                                    "SMS message",
                                    "Voice call",
                                ]
                            ),
                        ),
                        margin_top="2em",
                        margin_bottom="2em",
                    ),
                    spacing=".25em",
                ),
            ),
        ),
        pc.box(
            pc.button(pc.link("Login", href="/login")),
            pc.button(pc.link("Sign up", href="/signup")),
        ),
        background_image="/homepage_back.png",
    )


meta = [
    {"name": "theme_color", "content": "#FFFFFF"},
    {"char_set": "UTF-8"},
    {"property": "og:url", "content": "url"},
]

app = pc.App(state=entrance.EntranceState)

app.add_page(
    index,
    meta=meta,
    title="Bermen",
    description="A beautiful app built with Pynecone",
    image="/homepage_background.jpg",
)
app.add_page(
    entrance.log_in_session,
    route="/login",
    on_load=entrance.EntranceState.reload,
    title="Bermen Login Session",
)

app.add_page(
    entrance.sign_up_session,
    route="/signup",
    on_load=entrance.EntranceState.reload,
    title="Bermen Sign Up Session",
)

app.compile()
