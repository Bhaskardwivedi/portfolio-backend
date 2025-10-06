from django.http import JsonResponse
from .zoom_auth import get_zoom_token

def zoom_token_health(request):
    try:
        token = get_zoom_token()
        return JsonResponse({"ok": True, "has_token": bool(token)})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
