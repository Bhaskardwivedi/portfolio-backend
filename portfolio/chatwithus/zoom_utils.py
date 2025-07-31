import os
import requests
import base64
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")


def get_zoom_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ZOOM_ACCOUNT_ID}"
    
    auth_string = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    base64_auth = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Zoom token error:", response.text)
        return None


def create_zoom_meeting(topic="Client Meeting with Bhaskar", start_time="2025-06-02T12:30:00"):
    access_token = get_zoom_access_token()
    if not access_token:
        return None

    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
        "duration": 45,
        "timezone": "Asia/Kolkata"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json().get("join_url")
    else:
        print("Zoom meeting error:", response.text)
        return None
