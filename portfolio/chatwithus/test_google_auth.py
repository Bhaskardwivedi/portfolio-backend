# test_google_auth.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar"
]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)  # browser pops up
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("✅ token.json created/updated for this Google account.")

if __name__ == "__main__":
    main()
