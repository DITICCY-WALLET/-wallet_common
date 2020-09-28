import datetime

DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"


def date_to_timestamp(date, format=DEFAULT_FORMAT):
    return datetime.datetime.strptime(date, format).timestamp()


def now(is_str=True, format=DEFAULT_FORMAT):
    _now = datetime.datetime.now()
    if is_str:
        return _now.strftime(format)
    return _now






