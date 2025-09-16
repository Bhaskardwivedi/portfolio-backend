import os
import requests
import base64
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from portfolio.chatwithus.calendar_utils import create_calendar_event, send_meeting_invite

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

def get_start_time(minutes_from_now=10):
    start = datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ")

def create_zoom_meeting(topic="Client Meeting with Bhaskar", start_time=None, create_calendar_event=True, attendee_emails=None):
    """
    Create a Zoom meeting and optionally create Google Calendar event
    
    Args:
        topic: Meeting topic
        start_time: Meeting start time
        create_calendar_event: Whether to create calendar event
        attendee_emails: List of attendee emails for calendar invite
    
    Returns:
        Dict with meeting and calendar details
    """
    access_token = get_zoom_access_token()
    if not access_token:
        return None

    if not start_time:
        start_time = get_start_time(10)
    
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
        meeting_data = response.json()
        zoom_details = {
            "join_url": meeting_data.get("join_url"),
            "start_url": meeting_data.get("start_url"),
            "meeting_id": meeting_data.get("id"),
            "topic": meeting_data.get("topic"),
            "start_time": start_time
        }
        
        # Create calendar event if requested
        calendar_result = None
        if create_calendar_event:
            try:
                calendar_result = create_calendar_event(
                    meeting_data=zoom_details,
                    zoom_join_url=zoom_details["join_url"],
                    start_time=start_time
                )
                
                # Send meeting invite if attendees provided
                if attendee_emails:
                    send_meeting_invite(
                        meeting_data=zoom_details,
                        zoom_join_url=zoom_details["join_url"],
                        attendee_emails=attendee_emails,
                        start_time=start_time
                    )
                    
            except Exception as e:
                print(f"Calendar integration error: {e}")
                calendar_result = None
        
        return {
            "zoom": zoom_details,
            "calendar": calendar_result
        }
    else:
        print("Zoom meeting error:", response.text)
        return None
    

