import os

ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_HOST_EMAIL = os.getenv("ZOOM_HOST_EMAIL")

print("Zoom Account:", bool(ZOOM_ACCOUNT_ID))
print("Zoom Client ID:", bool(ZOOM_CLIENT_ID))
print("Zoom Secret:", bool(ZOOM_CLIENT_SECRET))
print("Zoom Host Email:", ZOOM_HOST_EMAIL)
