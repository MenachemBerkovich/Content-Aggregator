""""""
from pcconfig import config

import pynecone as pc

boxstyles = {
    "background": "white",
    "border": "1px solid #e5e5e5",
    "border_radius": "1em",
    "padding": "1em",
    "box_shadow": """
    rgba(17, 7, 53, 0.05) 0px 51px 78px 0px, rgba(17, 7, 53, 0.035) 0px 21.3066px 35.4944px 0px, rgba(17, 7, 53, 0.03) 0px 11.3915px 18.9418px 0px, rgba(17, 7, 53, 0.024) 0px 6.38599px 9.8801px 0px, rgba(17, 7, 53, 0.02) 0px 3.39155px 4.58665px 0px, rgba(17, 7, 53, 0.016) 0px 1.4113px 1.55262px 0px, rgba(41, 56, 78, 0.05) 0px 1px 0px 0px inset
    """,
    "height": "100%",
    "align_items": "left",
    "width": "100%",
    "min_height": "25em",
    "bg": "rgba(248, 248, 248, .75)",
    "_hover": {
        "box_shadow": """
        rgba(23, 6, 100, 0.035) 0px 24px 22px 0px, rgba(23, 6, 100, 0.055) 0px 8.5846px 8.03036px 0px, rgba(23, 6, 100, 0.067) 0px 4.77692px 3.89859px 0px, rgba(23, 6, 100, 0.082) 0px 2.63479px 1.91116px 0px, rgba(23, 6, 100, 0.12) 0px 1.15891px 0.755676px 0px
        """,
    },
}


def index() -> pc.Component:
    return pc.vstack(
        pc.text(
            "Welcome to the Bermen!",
            font_size=["2em", "3em", "3em", "4em"],
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
            pc.button("Sign in"),
            pc.button("Sign up"),
        ),
        background_image="/homepage_back.png",
    )


meta = [
    {"name": "theme_color", "content": "#FFFFFF"},
    {"char_set": "UTF-8"},
    {"property": "og:url", "content": "url"},
]

app = pc.App(state=pc.State)

app.add_page(
    index,
    meta=meta,
    title="Bermen",
    description="A beautiful app built with Pynecone",
    image="/homepage_background.jpg",
)
app.compile()
