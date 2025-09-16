from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Agar scope change karoge to token.json delete karna hoga
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.metadata",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar"
]

def main():
    creds = None
    
    # Check if credentials.json exists
    credentials_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    if not os.path.exists(credentials_path):
        print("❌ Error: credentials.json not found!")
        print(f"Please place your Google OAuth credentials file at: {credentials_path}")
        return
    
    # Token.json already hai?
    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Agar valid nahi hai to refresh/login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Error refreshing token: {e}")
                # Remove invalid token and re-authenticate
                if os.path.exists(token_path):
                    os.remove(token_path)
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save creds for next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print("✅ New authentication completed!")
            except Exception as e:
                print(f"❌ Error during authentication: {e}")
                return

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().getProfile(userId='me').execute()
        print("✅ Gmail connected as:", results['emailAddress'])
    except Exception as e:
        print(f"❌ Error accessing Gmail API: {e}")
        print("This might be due to insufficient permissions. Please check your OAuth scopes.")

if __name__ == '__main__':
    main()
