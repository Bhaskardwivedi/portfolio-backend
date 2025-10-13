import os
import requests
import json
from .zoom_auth import get_zoom_token

HOST_EMAIL = os.getenv("ZOOM_HOST_EMAIL")
TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
BASE_URL = os.getenv("ZOOM_BASE_URL", "https://api.zoom.us")

class ZoomApiError(RuntimeError):
    pass

def create_zoom_meeting(topic: str, start_iso: str, duration_min: int = 30) -> dict:

    if not HOST_EMAIL:
        raise ZoomApiError("ZOOM_HOST_EMAIL is not set")
        
    token = get_zoom_token()
    url = f"{BASE_URL}/v2/users/{HOST_EMAIL}/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-Type": "application/json",
    }

    payload = {
        "topic": topic or "Meeting",
        "type": 2,
        "start_time": start_iso,
        "duration": duration_min,
        "timezone": TIMEZONE,
        "settings": {
            "host_video": True,
            "participant_video": True
        }
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
