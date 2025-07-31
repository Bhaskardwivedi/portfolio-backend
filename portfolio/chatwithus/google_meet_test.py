from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
credentials = flow.run_local_server(port=0)

service = build("calendar", "v3", credentials=credentials)

event = {
    'summary': 'Meeting with Bhaskar',
    'start': {
        'dateTime': '2025-06-03T12:30:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
    'end': {
        'dateTime': '2025-06-03T13:00:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
    'conferenceData': {
        'createRequest': {
            'requestId': 'meet-123',
            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
        }
    },
    'attendees': [
        {'email': 'bhaskardwivedi544@gmail.com'}
    ],
}

event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()

print("✅ Google Meet Link:", event.get('hangoutLink'))
