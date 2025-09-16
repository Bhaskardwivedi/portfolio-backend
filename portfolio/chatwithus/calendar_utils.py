import os
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

def get_google_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, [
            "openid",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.metadata",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/calendar"
        ])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Google Calendar credentials not found or invalid")
    
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(meeting_data, zoom_join_url, start_time=None, duration_minutes=45):
    """
    Create a Google Calendar event for the Zoom meeting
    
    Args:
        meeting_data: Dict containing meeting info (topic, etc.)
        zoom_join_url: Zoom meeting join URL
        start_time: Meeting start time (ISO string or datetime)
        duration_minutes: Meeting duration in minutes
    
    Returns:
        Dict with event details or None if failed
    """
    try:
        service = get_google_calendar_service()
        
        # Parse start time
        if isinstance(start_time, str):
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = start_time or datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Convert to IST timezone
        ist_tz = pytz.timezone('Asia/Kolkata')
        start_ist = start_dt.astimezone(ist_tz)
        end_ist = start_ist + timedelta(minutes=duration_minutes)
        
        # Create event
        event = {
            'summary': meeting_data.get('topic', 'Client Meeting with Bhaskar'),
            'description': f"""
Zoom Meeting Details:
- Join URL: {zoom_join_url}
- Meeting ID: {meeting_data.get('meeting_id', 'N/A')}
- Duration: {duration_minutes} minutes

Please join the meeting using the link above.
            """.strip(),
            'start': {
                'dateTime': start_ist.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_ist.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'location': zoom_join_url,
            'attendees': [
                # Add attendees here if needed
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 15},       # 15 minutes before
                ],
            }
        }
        
        # Insert event
        event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'  # Send email notifications
        ).execute()
        
        return {
            'event_id': event['id'],
            'html_link': event['htmlLink'],
            'start_time': start_ist.isoformat(),
            'end_time': end_ist.isoformat()
        }
        
    except HttpError as error:
        print(f"Calendar API error: {error}")
        return None
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None

def send_meeting_invite(meeting_data, zoom_join_url, attendee_emails=None, start_time=None):
    """
    Send meeting invite via Gmail with calendar attachment
    
    Args:
        meeting_data: Dict containing meeting info
        zoom_join_url: Zoom meeting join URL
        attendee_emails: List of attendee email addresses
        start_time: Meeting start time
    
    Returns:
        Bool indicating success/failure
    """
    try:
        # First create calendar event
        calendar_result = create_calendar_event(meeting_data, zoom_join_url, start_time)
        if not calendar_result:
            return False
        
        # Generate .ics file content
        ics_content = generate_ics_file(meeting_data, zoom_join_url, start_time)
        
        # Send email with calendar attachment
        # This would integrate with your existing Gmail functionality
        # For now, return success if calendar event was created
        return True
        
    except Exception as e:
        print(f"Error sending meeting invite: {e}")
        return False

def generate_ics_file(meeting_data, zoom_join_url, start_time=None):
    """Generate .ics file content for calendar attachment"""
    if isinstance(start_time, str):
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    else:
        start_dt = start_time or datetime.now(timezone.utc) + timedelta(minutes=10)
    
    end_dt = start_dt + timedelta(minutes=45)
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Bhaskar Portfolio//Zoom Meeting//EN
BEGIN:VEVENT
UID:{meeting_data.get('meeting_id', 'meeting')}@bhaskar.portfolio
DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{meeting_data.get('topic', 'Client Meeting with Bhaskar')}
DESCRIPTION:Zoom Meeting\\nJoin URL: {zoom_join_url}
LOCATION:{zoom_join_url}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT15M
DESCRIPTION:Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""
    
    return ics_content
