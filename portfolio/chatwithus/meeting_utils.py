# portfolio/chatwithus/meeting_utils.py

# from .zoom_utils import create_zoom_meeting
# from .date_utils import parse_datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_google_meet(start_time: str, topic="Meeting with Bhaskar", description="", attendees=[]):
    """
    Create a Google Meet event with optional description & attendees.
    """
    creds = Credentials.from_authorized_user_file(
        os.path.join(os.path.dirname(__file__), "..", "..", "token.json"),
        SCOPES
    )
    service = build("calendar", "v3", credentials=creds)

    # Parse start time string
    start_dt = datetime.fromisoformat(start_time)
    end_dt = start_dt + timedelta(minutes=30)  # default 30 min meeting

    event = {
        "summary": topic,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [{"email": email} for email in attendees],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(datetime.now().timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    created_event = (
        service.events()
        .insert(calendarId="primary", body=event, conferenceDataVersion=1, sendUpdates="all")
        .execute()
    )

    return created_event.get("hangoutLink")


def send_meeting_invitation_email(attendee_email, meeting_link, topic, start_time, description=""):
    """
    Send a custom meeting invitation email using Gmail.
    """
    try:
        from .gmail_utils import send_email
        
        # Format the start time
        start_dt = datetime.fromisoformat(start_time)
        formatted_time = start_dt.strftime("%B %d, %Y at %I:%M %p")
        
        # Create email body
        email_body = f"""
Hello!

You have been invited to a meeting:

📅 Topic: {topic}
🕐 Time: {formatted_time}
🔗 Meeting Link: {meeting_link}

Description: {description}

Please click the link above to join the meeting.

Best regards,
Bhaskar
        """.strip()
        
        # Send email
        send_email(
            to=attendee_email,
            subject=f"Meeting Invitation: {topic}",
            body_text=email_body
        )
        
        return True
    except Exception as e:
        print(f"Error sending meeting invitation email: {e}")
        return False


# def schedule_meeting(query: str, platform="zoom", attendees=[]):
#     """
#     Schedule a meeting based on query & platform.
#     """
#     start_time = parse_datetime(query)
#     if not start_time:
#         return "❌ Could not understand the meeting time."
#
#     if platform.lower() == "zoom":
#         return create_zoom_meeting(start_time=start_time)
#     elif platform.lower() in ["google", "meet", "google meet"]:
#         return create_google_meet(start_time=start_time, attendees=attendees)
#     else:
#         return "❌ Unsupported platform. Please choose Zoom or Google Meet."
