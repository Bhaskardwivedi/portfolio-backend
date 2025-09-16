#!/usr/bin/env python3
"""
Simple test script for Zoom + Email functionality
Run this from the backend directory
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_zoom_meeting():
    """Test Zoom meeting creation"""
    print("🚀 Testing Zoom Meeting Creation...")
    
    try:
        from portfolio.chatwithus.zoom_utils import create_zoom_meeting
        
        # Create a simple meeting
        result = create_zoom_meeting(
            topic="Test Meeting - Simple Test",
            create_calendar_event=True
        )
        
        if result:
            print("✅ Zoom meeting created successfully!")
            print(f"   Meeting ID: {result['zoom']['meeting_id']}")
            print(f"   Join URL: {result['zoom']['join_url']}")
            
            if result['calendar']:
                print("✅ Calendar event created!")
                print(f"   Calendar Event ID: {result['calendar']['event_id']}")
            else:
                print("❌ Calendar event creation failed")
                
            return result
        else:
            print("❌ Zoom meeting creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_calendar_direct():
    """Test calendar functions directly"""
    print("\n📅 Testing Calendar Functions...")
    
    try:
        from portfolio.chatwithus.calendar_utils import create_calendar_event
        
        # Test data
        meeting_data = {
            "meeting_id": "test123",
            "topic": "Direct Calendar Test"
        }
        zoom_url = "https://zoom.us/j/test123"
        
        # Test calendar event creation
        calendar_result = create_calendar_event(
            meeting_data=meeting_data,
            zoom_join_url=zoom_url,
            start_time=None,
            duration_minutes=30
        )
        
        if calendar_result:
            print("✅ Calendar event created directly!")
            print(f"   Event ID: {calendar_result['event_id']}")
            print(f"   Calendar Link: {calendar_result['html_link']}")
        else:
            print("❌ Direct calendar creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run tests"""
    print("🧪 Simple Zoom + Calendar Test")
    print("=" * 40)
    
    # Test 1: Zoom meeting
    meeting = test_zoom_meeting()
    
    # Test 2: Calendar functions
    test_calendar_direct()
    
    print("\n" + "=" * 40)
    if meeting:
        print("✅ Zoom test: PASSED")
    else:
        print("❌ Zoom test: FAILED")
    
    print("✅ Calendar test: COMPLETED")

if __name__ == "__main__":
    main()
