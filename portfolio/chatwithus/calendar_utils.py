# portfolio/chatwithus/calendar_utils.py

import os
import uuid
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Calendar read/write scope
CAL_SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _google_service():
    """
    Build Google Calendar service using token.json (created via your auth step).
    Keep credentials.json & token.json at project root (manage.py folder).
    """
    creds = Credentials.from_authorized_user_file("token.json", CAL_SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)

def create_calendar_event(
    topic: str,
    start_iso_ist: str,
    duration_min: int,
    attendee_email: str | None,
    join_url: str,
    *,
    client_timezone: str | None = None,
    create_meet: bool = False,
) -> dict:
    """
    Create a Google Calendar event.

    Args:
        topic            : Event title
        start_iso_ist    : ISO datetime string with offset (e.g., '2025-10-12T19:30:00+05:30')
        duration_min     : Duration in minutes
        attendee_email   : Optional attendee to invite (sends calendar invite)
        join_url         : If Zoom, keep Zoom join link here (goes in location/description)
        client_timezone  : Optional IANA tz (e.g., 'America/New_York'). If given, start/end
                           will include explicit 'timeZone' so client sees local time correctly.
        create_meet      : If True, auto-generate a Google Meet link for this event.

    Returns:
        {
          "event_id": "...",
          "html_link": "https://calendar.google.com/...",
          "start": "...",
          "end": "...",
          "meet_link": "https://meet.google.com/..."  # present only if create_meet=True
        }
    """
    # 1) Compute start/end
    start_dt = datetime.fromisoformat(start_iso_ist)  # has offset -> tz-aware dt
    end_dt = start_dt + timedelta(minutes=int(duration_min))

    # 2) Base event body
    event = {
        "summary": topic or "Meeting",
        # If you're using Zoom, it's handy to keep the Zoom link in location + description
        "location": join_url or "",
        "description": f"Join link: {join_url}" if join_url else "Calendar event",
    }

    # 3) Time fields — with or without explicit timeZone
    if client_timezone:
        event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": client_timezone}
        event["end"]   = {"dateTime": end_dt.isoformat(),   "timeZone": client_timezone}
    else:
        # fallback: rely on offset embedded in ISO
        event["start"] = {"dateTime": start_dt.isoformat()}
        event["end"]   = {"dateTime": end_dt.isoformat()}

    # 4) Attendees (invitation email + calendar auto-add)
    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]

    # 5) Optional Google Meet link (conferenceData)
    if create_meet:
        event["conferenceData"] = {
            "createRequest": {
                "requestId": str(uuid.uuid4()),  # must be unique per insert
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    # 6) Insert event
    service = _google_service()
    created = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all",                 # emails attendees
        conferenceDataVersion=1 if create_meet else 0
    ).execute()

    # 7) Extract Meet link (if any)
    meet_link = created.get("hangoutLink")
    if not meet_link and create_meet:
        try:
            eps = created["conferenceData"]["entryPoints"]
            meet_link = next((ep["uri"] for ep in eps if ep.get("entryPointType") == "video"), None)
        except Exception:
            meet_link = None

    # 8) Return essentials
    return {
        "event_id": created.get("id"),
        "html_link": created.get("htmlLink"),
        "start": created["start"]["dateTime"],
        "end": created["end"]["dateTime"],
        **({"meet_link": meet_link} if create_meet else {}),
    }
