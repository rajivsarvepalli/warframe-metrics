"""Holds the utils required for common datetime functions."""
from typing import Dict

import datetime

def hour_minute_second_microsecond(time_delta: datetime.timedelta): Dict:
    """Converts a timedelta to a dictionary of hour, minute, second, and microsecond."""
    return {
        "hour": time_delta.seconds//3600,
        "minute": (time_delta.seconds//60)%60,
        "second": (time_delta.seconds)%60,
        "microsecond": time_delta.microseconds,
    }