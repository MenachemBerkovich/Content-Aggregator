"""_summary_#TODO docstring
"""


from __future__ import annotations
from datetime import time

from enum import Enum


class Timing(Enum):
    """Defined identities for timing types
    """
    DAILY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7
    SUNDAY = 8

#TODO add timezone to the schedule in Messenger and handle it as well by user.sending_time setter and getter.
class Time:
    """Time of messages sending, including hour, minute, and frequency.
    """
    def __init__(self, sending_time: time, sending_schedule: Timing) -> None:
        self.sending_time = sending_time
        self.sending_schedule = sending_schedule

    def __eq__(self, other: Time) -> bool:
        return (
            self.sending_time == other.sending_time
            and self.sending_schedule == other.sending_schedule
        )
