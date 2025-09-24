import dataclasses
import datetime

import pytz

timezone_choices = [(tz, tz) for tz in pytz.all_timezones]


half_hour_intervals = [
    datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    + i * datetime.timedelta(minutes=30)
    for i in range(48)
]


@dataclasses.dataclass
class TimeSlot:
    start: datetime.time
    end: datetime.time


time_slots = [
    TimeSlot(start=time.time(), end=(time + datetime.timedelta(minutes=30)).time())
    for time in half_hour_intervals
]


def is_timezone_valid(timezone_name):
    try:
        pytz.timezone(timezone_name)
        return True
    except pytz.UnknownTimeZoneError:
        return False
