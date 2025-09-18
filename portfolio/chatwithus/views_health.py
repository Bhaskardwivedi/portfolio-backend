import os
import requests
from requests.auth import HTTPBasicAuth

# 🔹 Railway me ye env vars set hone chahiye
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_HOST_EMAIL = os.getenv("ZOOM_HOST_EMAIL")  # e.g., assistant@bhaskarai.com

# Step 1: Token fetch
def get_zoom_token():
    url = "https://zoom.us/oauth/token"
    params = {"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID}
    auth = HTTPBasicAuth(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)

    resp = requests.post(url, params=params, auth=auth)
    resp.raise_for_status()
    return resp.json()["access_token"]

# Step 2: Meeting create
def create_meeting(token):
    url = f"https://api.zoom.us/v2/users/{ZOOM_HOST_EMAIL}/meetings"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "topic": "Test Meeting via API",
        "type": 1,  # 1 = instant meeting
        "settings": {
            "host_video": True,
            "participant_video": True
        }
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    try:
        token = get_zoom_token()
        meeting = create_meeting(token)
        print("✅ Meeting Created Successfully!")
        print("Join URL:", meeting["join_url"])
        print("Meeting ID:", meeting["id"])
    except Exception as e:
        print("❌ Error:", e)
