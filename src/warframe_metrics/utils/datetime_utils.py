import datetime

def hour_minute_second_microsecond(time_delta: datetime.timedelta):
    return {
        "hour": time_delta.seconds//3600,
        "minute": (time_delta.seconds//60)%60,
        "second": (time_delta.seconds)%60,
        "microsecond": time_delta.microseconds,
    }