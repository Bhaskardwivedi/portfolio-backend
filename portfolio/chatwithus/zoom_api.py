import os
import json
import requests
from .zoom_auth import get_zoom_token

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
HOST_EMAIL   = os.getenv("ZOOM_HOST_EMAIL")  # e.g., assistant@bhaskarai.com
DEFAULT_TZ   = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
BASE_RAW     = os.getenv("ZOOM_BASE_URL", "https://api.zoom.us").rstrip("/")

# Normalize to /v2 root
API_ROOT = BASE_RAW if BASE_RAW.endswith("/v2") else BASE_RAW + "/v2"


class ZoomApiError(RuntimeError):
    """Raised when Zoom API returns a non-2xx response."""
    pass


# ---------------------------------------------------------------------
# Create a scheduled Zoom meeting
#   topic:        meeting title
#   start_iso:    ISO datetime with offset (e.g., '2025-10-21T16:30:00-04:00')
#   duration_min: integer minutes
#   timezone:     IANA tz (e.g., 'America/New_York'); optional
# ---------------------------------------------------------------------
def create_zoom_meeting(
    topic: str,
    start_iso: str,
    duration_min: int = 30,
    timezone: str | None = None
) -> dict:
    if not HOST_EMAIL:
        raise ZoomApiError("ZOOM_HOST_EMAIL is not set in environment.")

    token = get_zoom_token()

    url = f"{API_ROOT}/users/{HOST_EMAIL}/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "topic": topic or "Meeting",
        "type": 2,                          # scheduled meeting
        "start_time": start_iso,            # ISO with offset
        "duration": int(duration_min),
        "timezone": timezone or DEFAULT_TZ, # IANA tz name
        "settings": {
            "host_video": True,
            "participant_video": True,
            # add other settings as needed:
            # "waiting_room": True,
            # "join_before_host": False,
        },
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
    if resp.status_code not in (200, 201):
        raise ZoomApiError(f"Create meeting failed ({resp.status_code}): {resp.text}")

    d = resp.json()
    return {
        "id": d.get("id"),
        "topic": d.get("topic"),
        "start_time": d.get("start_time"),
        "join_url": d.get("join_url"),
        "start_url": d.get("start_url"),
    }
