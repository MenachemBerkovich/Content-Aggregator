from datetime import time 
from enum import Enum


class Timing(Enum):
    DAILY = 1
    WEEKLY = 2

class Time:
    def __init__(self, sending_time: time, sending_schedule: Timing) -> None:
        self.sending_time = sending_time
        self.sending_schedule = sending_schedule
