from django.http import JsonResponse
import os

def env_health(request):
    return JsonResponse({
        "ZOOM_ACCOUNT_ID": bool(os.getenv("ZOOM_ACCOUNT_ID")),
        "ZOOM_CLIENT_ID": bool(os.getenv("ZOOM_CLIENT_ID")),
        "ZOOM_CLIENT_SECRET": bool(os.getenv("ZOOM_CLIENT_SECRET")),
        "ZOOM_HOST_EMAIL": os.getenv("ZOOM_HOST_EMAIL") or "MISSING"
    })
