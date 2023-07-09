"""User's sending_time management and presentation.
"""
from datetime import datetime

import pynecone as pc

from . import entrance
from contentaggregator.lib.user.userproperties import time


class SendingTimeDashboard(entrance.EntranceState):
    """Sending time state manager"""

    sending_time_reset_message: str = ""

    def save_changes(self) -> None:
        """Reset self._user.sending_time property."""
        if self._user:
            try:
                self._user.sending_time = time.Time(
                    datetime.strptime(self.send_hour, "%H:%M").time(),
                    time.Timing.__dict__[self.send_timing.upper()],
                )
                self.sending_time_reset_message = "Updated successfully!"
            except Exception as e:
                self.sending_time_reset_message = str(e)


def sending_time_presentation() -> pc.Component:
    """Generate a sending time reset box part an the dashboard page

    Returns:
        pc.Component: The component that will be displayed on the dashboard for sending time reset.
    """
    return pc.vstack(
        pc.text("Schedule a frequency and time of sending:", as_="b"),
        pc.vstack(
            pc.hstack(
                pc.select(
                    [key.name.capitalize() for key in time.Timing],
                    placeholder="Select timing",
                    default_value=SendingTimeDashboard.send_timing,
                    on_change=SendingTimeDashboard.set_send_timing,
                ),
                pc.input(
                    type_="time",
                    placeholder="Select hour",
                    default_value=SendingTimeDashboard.send_hour,
                    on_change=SendingTimeDashboard.set_send_hour,
                ),
            ),
            pc.button("Save", on_click=SendingTimeDashboard.save_changes),
            pc.text(SendingTimeDashboard.sending_time_reset_message),
            border_radius="15px",
            padding=5,
            border_color="black",
            border_width="thick",
        ),
    )
