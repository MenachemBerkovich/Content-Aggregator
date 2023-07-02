from datetime import datetime

import pynecone as pc

from . import entrance
from contentaggregator.lib.user.userproperties import time


class SendingTimeDashboard(entrance.EntranceState):
    sending_time_reset_message: str = ""

    def save_changes(self) -> None:
        if self._user:
            try:
                self._user.sending_time = time.Time(
                    datetime.strptime(self.send_hour, "%H:%M").time(),
                    time.Timing.__dict__[self.send_timing.upper()],
                )
            except Exception as e:
                print(e)
                self.sending_time_reset_message = str(e)
        print(
            type(self.send_timing),
            self.send_timing,
            type(self.send_hour),
            self.send_hour,
        )


def sending_time_presentation() -> pc.Component:
    return pc.vstack(
        pc.text("Schedule a frequency and time of sending:", as_="b"),
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
    )
