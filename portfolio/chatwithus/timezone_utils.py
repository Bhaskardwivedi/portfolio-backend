from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def parse_client_dt(date_str: str, time_str: str, fmt: str = "%Y-%m-%d %I:%M %p") -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", fmt)

def to_ist_iso(date_str: str, time_str: str, client_tz: str, time_fmt: str = "%Y-%m-%d %I:%M %p") -> str:

    client_zone = pytz.timezone(client_tz or "Asia/Kolkata")
    naive = parse_client_dt(date_str, time_str, time_fmt)
    client_local = client_zone.localize(naive)
    ist_dt = client_local.astimezone(IST)
    return ist_dt.isoformat()  

def parse_client_local(date_str: str, time_str: str, client_tz: str,
                       fmt: str = "%Y-%m-%d %I:%M %p"):
    tz = pytz.timezone(client_tz or "UTC")
    naive = datetime.strptime(f"{date_str} {time_str}", fmt)
    local_dt = tz.localize(naive)  # DST-safe
    return local_dt, tz