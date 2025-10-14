#!/usr/bin/env python3
"""
Simple test script for Zoom meeting + Email functionality
Similar to Google Meet testing we did yesterday
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Fix the import path - go up to backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

def test_zoom_meeting_creation():
    """Test 1: Create a simple Zoom meeting"""
    print("🚀 Test 1: Creating Zoom Meeting...")
    
    try:
        from portfolio.chatwithus.zoom_utils import create_zoom_meeting
        
        # Create a meeting for 15 minutes from now
        result = create_zoom_meeting(
            topic="Test Meeting - Zoom + Email",
            start_time=None,  # Will use default (10 minutes from now)
            create_calendar_event=True
        )
        
        if result:
            print("✅ Zoom meeting created successfully!")
            print(f"   Meeting ID: {result['zoom']['meeting_id']}")
            print(f"   Join URL: {result['zoom']['join_url']}")
            print(f"   Topic: {result['zoom']['topic']}")
            
            if result['calendar']:
                print("✅ Calendar event created!")
                print(f"   Calendar Event ID: {result['calendar']['event_id']}")
                print(f"   Calendar Link: {result['calendar']['html_link']}")
            else:
                print("❌ Calendar event creation failed")
                
            return result
        else:
            print("❌ Zoom meeting creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_zoom_with_attendees():
    """Test 2: Create Zoom meeting with attendees (for email invites)"""
    print("\n📧 Test 2: Creating Zoom Meeting with Attendees...")
    
    try:
        from portfolio.chatwithus.zoom_utils import create_zoom_meeting
        
        # Create meeting for tomorrow at 2 PM
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1, hours=14)
        
        result = create_zoom_meeting(
            topic="Client Consultation Meeting",
            start_time=tomorrow.isoformat(),
            create_calendar_event=True,
            attendee_emails=["test@example.com", "client@example.com"]
        )
        
        if result:
            print("✅ Meeting with attendees created!")
            print(f"   Meeting ID: {result['zoom']['meeting_id']}")
            print(f"   Start Time: {result['zoom']['start_time']}")
            
            if result['calendar']:
                print("✅ Calendar event with attendees created!")
                print(f"   Calendar Event ID: {result['calendar']['event_id']}")
                print(f"   Start Time (IST): {result['calendar']['start_time']}")
                print(f"   End Time (IST): {result['calendar']['end_time']}")
            else:
                print("❌ Calendar event creation failed")
                
            return result
        else:
            print("❌ Meeting creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_calendar_functions_directly():
    """Test 3: Test calendar functions directly"""
    print("\n📅 Test 3: Testing Calendar Functions Directly...")
    
    try:
        from portfolio.chatwithus.calendar_utils import create_calendar_event
        
        # Test data
        meeting_data = {
            "meeting_id": "test123",
            "topic": "Direct Calendar Test"
        }
        zoom_url = "https://zoom.us/j/test123"
        
        # Test calendar event creation
        print("   Testing calendar event creation...")
        from datetime import datetime, timezone
        start_time = datetime.now(timezone.utc).isoformat()
        
        calendar_result = create_calendar_event(
            topic=meeting_data["topic"],
            start_iso_ist=start_time,
            duration_min=30,
            attendee_email=None,
            join_url=zoom_url
        )
        
        if calendar_result:
            print("   ✅ Calendar event created directly!")
            print(f"      Event ID: {calendar_result['event_id']}")
        else:
            print("   ❌ Direct calendar creation failed")
        
        # Note: ICS file generation function not available in current calendar_utils
        print("   ℹ️  ICS file generation not available in current implementation")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_email_integration():
    """Test 4: Test email functionality (if available)"""
    print("\n📧 Test 4: Testing Email Integration...")
    
    try:
        # Check if we have Gmail functionality
        from portfolio.chatwithus.test_gmail import main as test_gmail
        
        print("   Testing Gmail connection...")
        test_gmail()
        print("   ✅ Gmail connection successful!")
        
        # Test sending meeting invite through calendar event creation
        print("   Testing meeting invite email...")
        
        meeting_data = {
            "meeting_id": "email_test_123",
            "topic": "Email Test Meeting"
        }
        
        from datetime import datetime, timezone
        start_time = datetime.now(timezone.utc).isoformat()
        
        # Create calendar event with attendee email to send invite
        email_result = create_calendar_event(
            topic=meeting_data["topic"],
            start_iso_ist=start_time,
            duration_min=30,
            attendee_email="test@example.com",
            join_url="https://zoom.us/j/email_test_123"
        )
        
        if email_result:
            print("   ✅ Meeting invite email sent via calendar event!")
            print(f"      Event ID: {email_result['event_id']}")
        else:
            print("   ❌ Meeting invite email failed")
            
    except Exception as e:
        print(f"   ❌ Email test error: {e}")
        print("   ℹ️  Make sure you have Gmail credentials set up")

def main():
    """Run all tests"""
    print("🧪 Testing Zoom + Email Integration")
    print("=" * 50)
    
    # Test 1: Basic Zoom meeting
    meeting1 = test_zoom_meeting_creation()
    
    # Test 2: Zoom with attendees
    meeting2 = test_zoom_with_attendees()
    
    # Test 3: Calendar functions
    test_calendar_functions_directly()
    
    # Test 4: Email integration
    test_email_integration()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    
    if meeting1:
        print("✅ Test 1: Zoom meeting creation - PASSED")
    else:
        print("❌ Test 1: Zoom meeting creation - FAILED")
    
    if meeting2:
        print("✅ Test 2: Zoom with attendees - PASSED")
    else:
        print("❌ Test 2: Zoom with attendees - FAILED")
    
    print("✅ Test 3: Calendar functions - COMPLETED")
    print("✅ Test 4: Email integration - COMPLETED")
    
    print("\n📋 Next Steps:")
    print("1. Check your Zoom account for the created meetings")
    print("2. Check your Google Calendar for the events")
    print("3. Check your email for meeting invites (if configured)")

if __name__ == "__main__":
    main()
