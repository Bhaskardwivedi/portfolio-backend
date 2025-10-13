# portfolio/chatwithus/views_zoom_api.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .zoom_api import create_zoom_meeting

@csrf_exempt
@require_POST
def zoom_test_create(request):
    """
    POST body example:
    {
      "topic": "Client Demo",
      "start_time": "2025-10-11T16:00:00+05:30",
      "duration": 45
    }
    """
    try:
        body = json.loads(request.body or "{}")
        topic = body.get("topic", "Client Discussion")
        start_iso = body["start_time"]            # required
        duration = int(body.get("duration", 45))  # default 45

        result = create_zoom_meeting(topic, start_iso, duration)
        return JsonResponse({"ok": True, **result}, status=201)

    except KeyError as e:
        return JsonResponse({"ok": False, "error": f"missing field: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
