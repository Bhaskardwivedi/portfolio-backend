#!/usr/bin/env python3
"""
Test script for Zoom + Google Calendar integration
"""

from zoom_utils import create_zoom_meeting
from datetime import datetime, timezone, timedelta

def test_zoom_calendar_integration():
    """Test the integrated Zoom + Calendar functionality"""
    
    print("🚀 Testing Zoom + Google Calendar Integration...")
    
    # Test 1: Create meeting with calendar event
    print("\n📅 Test 1: Creating Zoom meeting with calendar event...")
    result1 = create_zoom_meeting(
        topic="Test Meeting with Calendar Integration",
        start_time=None,  # Will use default (10 minutes from now)
        create_calendar_event=True
    )
    
    if result1:
        print("✅ Zoom meeting created successfully!")
        print(f"   Meeting ID: {result1['zoom']['meeting_id']}")
        print(f"   Join URL: {result1['zoom']['join_url']}")
        
        if result1['calendar']:
            print("✅ Calendar event created successfully!")
            print(f"   Calendar Event ID: {result1['calendar']['event_id']}")
            print(f"   Calendar Link: {result1['calendar']['html_link']}")
        else:
            print("❌ Calendar event creation failed")
    else:
        print("❌ Zoom meeting creation failed")
    
    # Test 2: Create meeting with specific time and attendees
    print("\n📅 Test 2: Creating meeting with specific time and attendees...")
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1, hours=10)  # 10 AM tomorrow
    
    result2 = create_zoom_meeting(
        topic="Scheduled Client Meeting",
        start_time=tomorrow.isoformat(),
        create_calendar_event=True,
        attendee_emails=["client@example.com", "team@example.com"]
    )
    
    if result2:
        print("✅ Scheduled meeting created successfully!")
        print(f"   Meeting ID: {result2['zoom']['meeting_id']}")
        print(f"   Start Time: {result2['zoom']['start_time']}")
        
        if result2['calendar']:
            print("✅ Calendar event created with attendees!")
            print(f"   Calendar Event ID: {result2['calendar']['event_id']}")
        else:
            print("❌ Calendar event creation failed")
    else:
        print("❌ Scheduled meeting creation failed")
    
    # Test 3: Create meeting without calendar event
    print("\n📅 Test 3: Creating Zoom meeting without calendar event...")
    result3 = create_zoom_meeting(
        topic="Quick Meeting (No Calendar)",
        create_calendar_event=False
    )
    
    if result3:
        print("✅ Zoom meeting created (no calendar event)")
        print(f"   Meeting ID: {result3['zoom']['meeting_id']}")
        print(f"   Calendar: {result3['calendar']}")
    else:
        print("❌ Meeting creation failed")

if __name__ == "__main__":
    test_zoom_calendar_integration()
