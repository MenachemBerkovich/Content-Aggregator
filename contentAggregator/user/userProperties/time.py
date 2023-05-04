"""_summary_
"""


from __future__ import annotations
from datetime import time
from enum import Enum


class Timing(Enum):
    """Defined identities for timing types
    """
    DAILY = 1
    WEEKLY = 2


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
