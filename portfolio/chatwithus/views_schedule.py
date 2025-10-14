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

SENDER_EMAIL = os.getenv("ZOOM_HOST_EMAIL")  # assistant@bhaskarai.com


def _google_files_present() -> bool:
    """Check if Google auth files exist (so Calendar/Meet can work)."""
    return os.path.exists("credentials.json") and os.path.exists("token.json")


@csrf_exempt
@require_POST
def schedule_meeting(request):
    """
    POST JSON:
    {
      "platform": "zoom" | "meet",
      "topic": "Discovery Call",
      "date": "2025-10-22",
      "time": "03:30 PM",                  # 12h format; if you want 24h, parse in parse_client_local
      "client_timezone": "America/New_York",
      "duration": 45,
      "email": "client@example.com"        # optional
    }
    """
    try:
        try:
            b = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "Invalid JSON body"}, status=400)

        # ---- Required fields
        for key in ("date", "time"):
            if key not in b:
                return JsonResponse({"ok": False, "error": f"missing field: '{key}'"}, status=400)

        platform = str(b.get("platform", "zoom")).strip().lower()
        topic = b.get("topic", "Client Meeting")
        date_ = b["date"]
        time_ = b["time"]
        tz_name = b.get("client_timezone", "Asia/Kolkata")
        duration = int(b.get("duration", 45))
        attendee_email = b.get("email")

        # 1) client local -> aware datetimes
        client_dt, _tzinfo = parse_client_local(date_, time_, tz_name)
        end_dt = client_dt + timedelta(minutes=duration)
        start_iso_local = client_dt.isoformat()
        end_iso_local = end_dt.isoformat()

        result = {
            "ok": True,
            "platform": platform,
            "topic": topic,
            "duration": duration,
            "when_client_local": client_dt.strftime(f"%d %b %Y, %I:%M %p {tz_name}"),
        }

        # 2) platform handling
        join_link = None
        calendar = None

        if platform == "zoom":
            # Create Zoom meeting (now supports timezone arg)
            zoom = create_zoom_meeting(topic, start_iso_local, duration, timezone=tz_name)
            result["zoom"] = zoom
            join_link = zoom.get("join_url")

            # Optional calendar (add Zoom link to calendar event)
            if _google_files_present():
                try:
                    calendar = create_calendar_event(
                        topic=topic,
                        start_iso_ist=start_iso_local,     # client-local ISO with offset
                        duration_min=duration,
                        attendee_email=attendee_email,
                        join_url=join_link,
                        client_timezone=tz_name,
                        create_meet=False                   # We're using Zoom
                    )
                except Exception as e:
                    calendar = {"error": f"calendar failed: {e}"}
            else:
                calendar = {"skipped": "Google credentials/token not found"}

        elif platform in ("meet", "google_meet", "google meet"):
            if not _google_files_present():
                return JsonResponse(
                    {"ok": False, "error": "Meet creation failed: Google credentials/token not found on server"},
                    status=500
                )
            # Create Google Calendar event with Meet link
            try:
                calendar = create_calendar_event(
                    topic=topic,
                    start_iso_ist=start_iso_local,
                    duration_min=duration,
                    attendee_email=attendee_email,
                    join_url="",                       # not needed for Meet
                    client_timezone=tz_name,
                    create_meet=True
                )
                join_link = calendar.get("meet_link")
            except Exception as e:
                return JsonResponse({"ok": False, "error": f"meet creation failed: {e}"}, status=500)

        else:
            return JsonResponse({"ok": False, "error": "Unsupported platform. Use 'zoom' or 'meet'."}, status=400)

        # 3) Friendly IST time mirror (best-effort)
        try:
            import pytz
            ist = pytz.timezone("Asia/Kolkata")
            result["when_ist"] = client_dt.astimezone(ist).strftime("%d %b %Y, %I:%M %p IST")
        except Exception:
            pass

        # 4) Optional confirmation email from assistant@bhaskarai.com
        mail = None
        if attendee_email and join_link:
            try:
                cal_link = (calendar or {}).get("html_link")
                mail = send_invite_email(
                    sender_email=SENDER_EMAIL or "me",
                    to_email=attendee_email,
                    subject=topic,
                    join_url=join_link,
                    calendar_link=cal_link,
                    # NOTE: this is client local ISO; rename param in gmail_utils if needed
                    start_ist_iso=start_iso_local
                )
            except Exception as e:
                mail = {"error": f"email failed: {e}"}

        result["calendar"] = calendar
        result["email"] = mail
        result["join_link"] = join_link

        return JsonResponse(result, status=201)

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
