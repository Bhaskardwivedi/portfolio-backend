#!/usr/bin/env python3
"""
Test Railway environment variables and Zoom API connection
"""

import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_railway_environment():
    """Check if we're running on Railway and what credentials we have"""
    print("🚂 Checking Railway Environment...")
    print("=" * 50)
    
    # Check if we're on Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    print(f"Running on Railway: {'✅ Yes' if is_railway else '❌ No'}")
    
    # Check Zoom credentials
    zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
    zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
    zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    
    print(f"\n🔍 Zoom Credentials:")
    print(f"ZOOM_ACCOUNT_ID: {'✅ Set' if zoom_account_id else '❌ Missing'}")
    if zoom_account_id:
        print(f"   Value: {zoom_account_id[:10]}...")
    
    print(f"ZOOM_CLIENT_ID: {'✅ Set' if zoom_client_id else '❌ Missing'}")
    if zoom_client_id:
        print(f"   Value: {zoom_client_id[:10]}...")
    
    print(f"ZOOM_CLIENT_SECRET: {'✅ Set' if zoom_client_secret else '❌ Missing'}")
    if zoom_client_secret:
        print(f"   Value: {zoom_client_secret[:10]}...")
    
    # Check other environment variables
    print(f"\n🌐 Other Environment Variables:")
    print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"PORT: {os.getenv('PORT', 'Not set')}")
    print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    
    return all([zoom_account_id, zoom_client_id, zoom_client_secret])

def test_zoom_api_connection():
    """Test Zoom API connection with current credentials"""
    print("\n🧪 Testing Zoom API Connection...")
    
    try:
        # Get credentials
        zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
        zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        
        if not all([zoom_account_id, zoom_client_id, zoom_client_secret]):
            print("❌ Cannot test connection - credentials missing")
            return False
        
        # Try to get access token
        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={zoom_account_id}"
        
        auth_string = f"{zoom_client_id}:{zoom_client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        base64_auth = base64.b64encode(auth_bytes).decode("utf-8")

        headers = {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        print("   Making request to Zoom API...")
        print(f"   URL: {url}")
        print(f"   Account ID: {zoom_account_id}")
        print(f"   Client ID: {zoom_client_id[:10]}...")
        
        response = requests.post(url, headers=headers)
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Zoom API connection successful!")
            token_data = response.json()
            print(f"   Access token received: {token_data.get('access_token', '')[:20]}...")
            print(f"   Token type: {token_data.get('token_type', 'N/A')}")
            print(f"   Expires in: {token_data.get('expires_in', 'N/A')} seconds")
            return True
        else:
            print(f"❌ Zoom API connection failed!")
            print(f"   Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"   Error: {error_data['error']}")
                if 'reason' in error_data:
                    print(f"   Reason: {error_data['reason']}")
            except:
                pass
                
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_zoom_meeting():
    """Test creating a simple Zoom meeting"""
    print("\n🎯 Testing Simple Zoom Meeting Creation...")
    
    try:
        from portfolio.chatwithus.zoom_utils import create_zoom_meeting
        
        print("   Creating test meeting...")
        result = create_zoom_meeting(
            topic="Railway Test Meeting",
            create_calendar_event=False  # Skip calendar for now
        )
        
        if result:
            print("✅ Zoom meeting created successfully!")
            print(f"   Meeting ID: {result['zoom']['meeting_id']}")
            print(f"   Join URL: {result['zoom']['join_url']}")
            return True
        else:
            print("❌ Zoom meeting creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚂 Railway Environment + Zoom API Test")
    print("=" * 60)
    
    # Check environment
    creds_ok = check_railway_environment()
    
    if creds_ok:
        print("\n✅ All credentials are set!")
        
        # Test Zoom API connection
        api_ok = test_zoom_api_connection()
        
        if api_ok:
            # Test meeting creation
            meeting_ok = test_simple_zoom_meeting()
            
            print("\n" + "=" * 60)
            print("🎯 Final Results:")
            print(f"✅ Environment: PASSED")
            print(f"✅ Zoom API: PASSED")
            print(f"{'✅' if meeting_ok else '❌'} Meeting Creation: {'PASSED' if meeting_ok else 'FAILED'}")
            
            if meeting_ok:
                print("\n🎉 Everything is working! You can now:")
                print("1. Create Zoom meetings")
                print("2. Integrate with Google Calendar")
                print("3. Send meeting invites via email")
            else:
                print("\n🔧 Meeting creation failed - check the error above")
        else:
            print("\n❌ Zoom API connection failed - check your credentials")
    else:
        print("\n❌ Missing credentials - check your Railway environment variables")
    
    print("\n📋 Next Steps:")
    print("1. If credentials are missing, update them in Railway dashboard")
    print("2. If API fails, verify your Zoom app settings")
    print("3. If meeting creation fails, check the error details above")

if __name__ == "__main__":
    main()
