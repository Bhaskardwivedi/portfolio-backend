#!/usr/bin/env python3
"""
Check Zoom API credentials
Run this to verify your Zoom setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_zoom_credentials():
    """Check if Zoom credentials are properly set"""
    print("🔍 Checking Zoom API Credentials...")
    print("=" * 50)
    
    # Check each credential
    zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
    zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
    zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    
    print(f"ZOOM_ACCOUNT_ID: {'✅ Set' if zoom_account_id else '❌ Missing'}")
    if zoom_account_id:
        print(f"   Value: {zoom_account_id[:10]}...")
    
    print(f"ZOOM_CLIENT_ID: {'✅ Set' if zoom_client_id else '❌ Missing'}")
    if zoom_client_id:
        print(f"   Value: {zoom_client_id[:10]}...")
    
    print(f"ZOOM_CLIENT_SECRET: {'✅ Set' if zoom_client_secret else '❌ Missing'}")
    if zoom_client_secret:
        print(f"   Value: {zoom_client_secret[:10]}...")
    
    print("\n" + "=" * 50)
    
    if all([zoom_account_id, zoom_client_id, zoom_client_secret]):
        print("✅ All Zoom credentials are set!")
        print("\n🔧 Next steps:")
        print("1. Verify these credentials in your Zoom App Marketplace")
        print("2. Make sure your Zoom app has the right permissions")
        print("3. Try running the Zoom test again")
    else:
        print("❌ Some Zoom credentials are missing!")
        print("\n🔧 How to fix:")
        print("1. Go to https://marketplace.zoom.us/")
        print("2. Sign in with your Zoom account")
        print("3. Create a new app or check existing app")
        print("4. Copy the credentials to your .env file")
        print("\n📝 Example .env file:")
        print("ZOOM_ACCOUNT_ID=your_account_id_here")
        print("ZOOM_CLIENT_ID=your_client_id_here")
        print("ZOOM_CLIENT_SECRET=your_client_secret_here")

def test_zoom_connection():
    """Test if we can connect to Zoom API"""
    print("\n🧪 Testing Zoom API Connection...")
    
    try:
        import requests
        
        # Get credentials
        zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
        zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        
        if not all([zoom_account_id, zoom_client_id, zoom_client_secret]):
            print("❌ Cannot test connection - credentials missing")
            return
        
        # Try to get access token
        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={zoom_account_id}"
        
        import base64
        auth_string = f"{zoom_client_id}:{zoom_client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        base64_auth = base64.b64encode(auth_bytes).decode("utf-8")

        headers = {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        print("   Making request to Zoom API...")
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Zoom API connection successful!")
            token_data = response.json()
            print(f"   Access token received: {token_data.get('access_token', '')[:20]}...")
        else:
            print(f"❌ Zoom API connection failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")

if __name__ == "__main__":
    check_zoom_credentials()
    test_zoom_connection()
