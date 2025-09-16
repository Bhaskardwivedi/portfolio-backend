import dateparser
from datetime import datetime

def parse_datetime(text: str, timezone: str = "Asia/Kolkata") -> str:

    dt = dateparser.parse(text, settings={"TIMEZONE": timezone, "RETURN_AS_TIMEZONE_AWARE": True})
    if not dt:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
