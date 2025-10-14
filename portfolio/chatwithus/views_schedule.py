import json
import os
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .timezone_utils import parse_client_local
from .zoom_api import create_zoom_meeting
from .calendar_utils import create_calendar_event
from .gmail_utils import send_invite_email

SENDER_EMAIL = os.getenv("ZOOM_HOST_EMAIL")  # sender mailbox (assistant@bhaskarai.com)


@csrf_exempt
@require_POST
def schedule_meeting(request):
    """
    POST JSON Example:
    {
      "platform": "zoom" or "meet",
      "topic": "Discovery Call",
      "date": "2025-10-12",
      "time": "04:00 PM",
      "client_timezone": "America/New_York",
      "duration": 45,
      "email": "client@example.com"
    }
    """
    try:
        b = json.loads(request.body or "{}")

        platform = b.get("platform", "zoom").lower()
        date_ = b["date"]
        time_ = b["time"]
        tz_name = b.get("client_timezone", "Asia/Kolkata")
        topic = b.get("topic", "Client Meeting")
        duration = int(b.get("duration", 45))
        attendee_email = b.get("email")

        # 1️⃣ Parse client local → aware datetime
        client_dt, tzinfo = parse_client_local(date_, time_, tz_name)
        end_dt = client_dt + timedelta(minutes=duration)
        start_iso_local = client_dt.isoformat()
        end_iso_local = end_dt.isoformat()

        # 2️⃣ Initialize response container
        result = {"ok": True, "platform": platform}

        # 3️⃣ Platform-specific logic
        if platform == "zoom":
            # ---- Zoom ----
            zoom = create_zoom_meeting(topic, start_iso_local, duration, timezone=tz_name)
            result["zoom"] = zoom

            # Calendar event (Zoom link in description)
            try:
                cal = create_calendar_event(
                    topic=topic,
                    start_iso_ist=start_iso_local,
                    duration_min=duration,
                    attendee_email=attendee_email,
                    join_url=zoom["join_url"],
                    client_timezone=tz_name,
                    create_meet=False
                )
            except Exception as e:
                cal = {"error": f"calendar failed: {e}"}
            result["calendar"] = cal
            join_link = zoom["join_url"]

        elif platform in ("meet", "google meet", "google_meet"):
            # ---- Google Meet ----
            try:
                cal = create_calendar_event(
                    topic=topic,
                    start_iso_ist=start_iso_local,
                    duration_min=duration,
                    attendee_email=attendee_email,
                    join_url="",                     # not needed
                    client_timezone=tz_name,
                    create_meet=True                  # generate Meet link
                )
                result["calendar"] = cal
                join_link = cal.get("meet_link")
            except Exception as e:
                return JsonResponse({"ok": False, "error": f"meet creation failed: {e}"}, status=500)

        else:
            return JsonResponse({"ok": False, "error": "Unsupported platform. Use 'zoom' or 'meet'."}, status=400)

        # 4️⃣ Email confirmation
        mail = None
        if attendee_email:
            try:
                cal_link = (result.get("calendar") or {}).get("html_link")
                mail = send_invite_email(
                    sender_email=SENDER_EMAIL or "me",
                    to_email=attendee_email,
                    subject=topic,
                    join_url=join_link,
                    calendar_link=cal_link,
                    start_ist_iso=start_iso_local
                )
            except Exception as e:
                mail = {"error": f"email failed: {e}"}
        result["email"] = mail

        # 5️⃣ Add friendly time summary
        try:
            import pytz
            ist = pytz.timezone("Asia/Kolkata")
            result["when_client_local"] = client_dt.strftime(f"%d %b %Y, %I:%M %p {tz_name}")
            result["when_ist"] = client_dt.astimezone(ist).strftime("%d %b %Y, %I:%M %p IST")
        except Exception:
            pass

        return JsonResponse(result, status=201)

    except KeyError as e:
        return JsonResponse({"ok": False, "error": f"missing field: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
