"""Dashboard package for packaging all user settings displayed on the dashboard.
"""
import pynecone as pc

from .. import entrance
from . import username_management
from . import password_management
from . import feeds_management
from . import addresses_management
from . import sending_time_management


def landing() -> pc.Component:
    """Generates user dashboard page.

    Returns:
        pc.Component: The vstack contains all nested components, for full dashboard presentation.
    """
    return pc.cond(
        entrance.EntranceState.is_authenticated,
        pc.vstack(
            username_management.username_presentation(),
            password_management.password_presentation(),
            feeds_management.feeds_presentation(),
            addresses_management.addresses_presentation(),
            sending_time_management.sending_time_presentation(),
        ),
        pc.hstack(
            pc.text("403:( You need"),
            pc.link("login", href="/login", as_="b"),
            pc.text(" or "),
            pc.link("sign up", href="/signup", as_="b"),
        ),
    )


class DashboardState(entrance.EntranceState):
    """Dashboard state. inherit from main EntranceState.
    """
    def reload_dashboard(self) -> None:
        """Resets dashboard classes vars when dashboard page is reloaded.
        """
        # reload username state
        username_management.DashboardUsernameState.new_username = ""
        username_management.DashboardUsernameState.username_reset_message = ""
        # reload password state
        password_management.DashboardPasswordState.old_password = ""
        password_management.DashboardPasswordState.new_password = ""
        password_management.DashboardPasswordState.new_password_confirmation = ""
        password_management.DashboardPasswordState.password_reset_message = ""
        # reload feeds state
        feeds_management.FeedsDashboardState.feeds_reset_delete_message = ""
        feeds_management.FeedsDashboardState.feeds_reset_add_message = ""
        feeds_management.FeedsDashboardState.is_addition_disabled = True
        feeds_management.FeedsDashboardState.is_deletion_disabled = True
        # reload addresses state
        addresses_management.AddressesDashboardState.email_address = ""
        addresses_management.AddressesDashboardState.email_address_reset_message = ""
        addresses_management.AddressesDashboardState.whatsapp_address_reset_message = ""
        addresses_management.AddressesDashboardState.phone_address_reset_message = ""
        addresses_management.AddressesDashboardState.sms_address_reset_message = ""
