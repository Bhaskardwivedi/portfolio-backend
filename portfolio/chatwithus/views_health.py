import os
import requests
from django.http import JsonResponse

# 🔹 Env Vars from Railway
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_HOST_EMAIL = os.getenv("ZOOM_HOST_EMAIL")  # ✅ Added

# 🔹 Get Zoom Access Token
def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    payload = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID
    }
    response = requests.post(
        url,
        data=payload,
        auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
    )
    data = response.json()
    return data.get("access_token")


# 🔹 Health Check Endpoint
def env_health(request):
    env_status = {
        "ZOOM_ACCOUNT_ID": bool(ZOOM_ACCOUNT_ID),
        "ZOOM_CLIENT_ID": bool(ZOOM_CLIENT_ID),
        "ZOOM_CLIENT_SECRET": bool(ZOOM_CLIENT_SECRET),
        "ZOOM_HOST_EMAIL": ZOOM_HOST_EMAIL if ZOOM_HOST_EMAIL else "MISSING"
    }
    return JsonResponse(env_status)


# 🔹 Create Zoom Meeting Endpoint
def create_zoom_meeting(request):
    try:
        token = get_zoom_access_token()
        if not token:
            return JsonResponse({"error": "Failed to get access token"}, status=400)

        url = f"https://api.zoom.us/v2/users/{ZOOM_HOST_EMAIL}/meetings"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "topic": "Test Meeting from Django",
            "type": 1,  # instant meeting
            "settings": {"host_video": True, "participant_video": True}
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        return JsonResponse({
            "status": "success" if response.status_code == 201 else "failed",
            "response": data
        }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
