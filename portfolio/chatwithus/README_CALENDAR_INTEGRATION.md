# Zoom + Google Calendar Integration

This module provides seamless integration between Zoom meetings and Google Calendar, allowing you to automatically create calendar events when Zoom meetings are scheduled.

## Features

✅ **Automatic Calendar Events**: Creates Google Calendar events for every Zoom meeting  
✅ **Meeting Invites**: Sends calendar invites to attendees  
✅ **ICS File Generation**: Generates .ics files for calendar attachments  
✅ **Timezone Support**: Handles IST timezone conversion  
✅ **Flexible Scheduling**: Supports immediate and scheduled meetings  
✅ **Error Handling**: Graceful fallback if calendar creation fails  

## Setup Requirements

### 1. Google API Credentials
- Place your `credentials.json` file in the `backend/` directory
- Ensure it has Calendar API access enabled
- Run `test_gmail.py` first to authenticate and generate `token.json`

### 2. Environment Variables
```bash
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

### 3. Dependencies
```bash
pip install google-api-python-client google-auth-oauthlib pytz
```

## Usage Examples

### Basic Meeting Creation with Calendar
```python
from chatwithus.zoom_utils import create_zoom_meeting

# Create meeting with automatic calendar event
result = create_zoom_meeting(
    topic="Client Consultation",
    create_calendar_event=True
)

if result:
    print(f"Meeting ID: {result['zoom']['meeting_id']}")
    print(f"Calendar Event ID: {result['calendar']['event_id']}")
```

### Scheduled Meeting with Attendees
```python
from datetime import datetime, timezone, timedelta

# Schedule meeting for tomorrow at 2 PM
tomorrow = datetime.now(timezone.utc) + timedelta(days=1, hours=14)

result = create_zoom_meeting(
    topic="Project Discussion",
    start_time=tomorrow.isoformat(),
    create_calendar_event=True,
    attendee_emails=["client@example.com", "team@example.com"]
)
```

### Meeting Without Calendar Event
```python
# Create Zoom meeting only (no calendar event)
result = create_zoom_meeting(
    topic="Quick Sync",
    create_calendar_event=False
)
```

## API Response Structure

```python
{
    "zoom": {
        "meeting_id": "123456789",
        "join_url": "https://zoom.us/j/123456789",
        "start_url": "https://zoom.us/s/123456789",
        "topic": "Meeting Topic",
        "start_time": "2025-01-15T10:00:00Z"
    },
    "calendar": {
        "event_id": "abc123def456",
        "html_link": "https://calendar.google.com/event?eid=...",
        "start_time": "2025-01-15T15:30:00+05:30",
        "end_time": "2025-01-15T16:15:00+05:30"
    }
}
```

## Django Integration

### 1. API Endpoint
```python
# urls.py
from chatwithus.usage_examples import create_meeting_api

urlpatterns = [
    path('api/create-meeting/', create_meeting_api, name='create_meeting_api'),
]
```

### 2. Form View
```python
# views.py
from chatwithus.usage_examples import create_meeting_view

# Add to your URL patterns
```

### 3. Contact Form Integration
```python
# When someone submits a contact form
from chatwithus.usage_examples import create_meeting_from_contact

contact_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'message': 'I need consultation',
    'preferred_time': '2025-01-16T14:00:00'
}

result = create_meeting_from_contact(contact_data)
```

## Testing

Run the test script to verify everything works:
```bash
cd backend/portfolio/chatwithus/
python test_calendar_integration.py
```

## Error Handling

The system gracefully handles errors:
- If calendar creation fails, the Zoom meeting is still created
- If Zoom creation fails, nothing is created
- All errors are logged for debugging

## Customization

### Calendar Event Details
Modify `calendar_utils.py` to customize:
- Event description format
- Reminder settings
- Timezone handling
- Attendee management

### Meeting Settings
Modify `zoom_utils.py` to customize:
- Default meeting duration
- Meeting type (instant vs scheduled)
- Password requirements
- Waiting room settings

## Troubleshooting

### Common Issues

1. **"Credentials not found"**
   - Ensure `credentials.json` is in the correct location
   - Run `test_gmail.py` to authenticate

2. **"Calendar API error"**
   - Check if Calendar API is enabled in Google Cloud Console
   - Verify OAuth scopes include calendar permissions

3. **"Zoom token error"**
   - Verify Zoom API credentials in environment variables
   - Check Zoom account permissions

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG_CALENDAR=true
```

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Use environment variables for sensitive data
- Regularly rotate API keys and tokens
- Implement rate limiting for production use

## Support

For issues or questions:
1. Check the error logs
2. Verify API credentials and permissions
3. Test with the provided test scripts
4. Ensure all dependencies are installed
