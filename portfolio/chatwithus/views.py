# chatwithus/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
import traceback

from .agent import generate_smart_reply
from .zoom_utils import create_zoom_meeting
from .models import ChatSession


class ChatMessageAPIView(APIView):
    conversation_memory = {}

    def post(self, request):
        try:
            session_id = request.GET.get("session_id", "anon").strip()

            # 🆕 Reset session if new_session param given
            if request.GET.get("new_session") == "true":
                ChatSession.objects.filter(session_id=session_id).delete()
                self.conversation_memory.pop(session_id, None)

            # ✅ Parse incoming data
            data = request.data[0] if isinstance(request.data, list) else request.data
            if not isinstance(data, dict):
                return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

            name = data.get("name", "").strip()
            email = data.get("email", "").strip().lower()
            user_message = data.get("message", "").strip()

            if not user_message:
                return Response({"error": "Missing message"}, status=status.HTTP_400_BAD_REQUEST)

            # 📂 Get or create session
            chat_session, _ = ChatSession.objects.get_or_create(session_id=session_id)

            # Save name/email if first time
            if name and not chat_session.name:
                chat_session.name = name
            if email and not chat_session.email:
                chat_session.email = email

            # Default values if not set
            defaults = {
                "message_count": 0,
                "meeting_stage": None,
                "platform_selected": None,
                "requirement_confirmed": False,
                "last_intent": None
            }
            for field, default in defaults.items():
                if getattr(chat_session, field, None) is None:
                    setattr(chat_session, field, default)

            chat_session.message_count += 1
            chat_session.save()

            # 🔹 Step 1 — Ask Name
            if not chat_session.name:
                return Response({"bot_reply": "May I know your name?"})

            # 🔹 Step 2 — Ask Email
            if not chat_session.email:
                return Response({"bot_reply": f"Thanks {chat_session.name}! Could you share your email so I can follow up?"})

            # 🔹 Step 3 — Requirement Confirmation
            requirement_keywords = ["need", "want", "require", "looking for", "build", "develop", "create"]
            if any(k in user_message.lower() for k in requirement_keywords) and not chat_session.requirement_confirmed:
                chat_session.last_intent = "confirm_requirement"
                chat_session.temp_requirement = user_message
                chat_session.save()
                return Response({"bot_reply": f"Got it, {chat_session.name}. So you’re looking for {user_message}, right?"})

            if chat_session.last_intent == "confirm_requirement" and user_message.lower() in ["yes", "yep", "sure", "ok"]:
                chat_session.requirement_confirmed = True
                chat_session.last_intent = None
                chat_session.meeting_stage = "ask_platform"
                chat_session.save()

                # Send requirement email to owner
                send_mail(
                    subject="New Client Requirement Received",
                    message=f"Client: {chat_session.name}\nEmail: {chat_session.email}\nRequirement: {getattr(chat_session, 'temp_requirement', '')}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True
                )

                return Response({"bot_reply": "Perfect! Would you like to connect over Zoom or Google Meet?"})

            # 🔹 Step 4 — Meeting Platform (more human-like)
            if chat_session.meeting_stage == "ask_platform":
                msg_lower = user_message.lower()

                if "zoom" in msg_lower:
                    chat_session.platform_selected = "Zoom"
                    chat_session.meeting_stage = "ask_time"
                    chat_session.save()
                    return Response({"bot_reply": "Great! Please share a suitable date & time for the Zoom meeting."})
                elif "google meet" in msg_lower or "meet" in msg_lower:
                    chat_session.platform_selected = "Google Meet"
                    chat_session.meeting_stage = "ask_time"
                    chat_session.save()
                    return Response({"bot_reply": "Got it! Please share a suitable date & time for the Google Meet."})
                elif any(word in msg_lower for word in ["bhaskar", "project", "skill", "capable"]):
                    return Response({"bot_reply": "Bhaskar is an experienced AI & automation developer with multiple successful projects delivered. Now, would you prefer Zoom or Google Meet?"})
                elif any(word in msg_lower for word in ["need", "require", "details", "more info"]):
                    # Save extra details to send in meeting email later
                    chat_session.extra_details = user_message
                    chat_session.save()
                    return Response({"bot_reply": "Thanks for sharing the details. Would you like to proceed with Zoom or Google Meet?"})
                else:
                    return Response({"bot_reply": "Please choose Zoom or Google Meet."})

            # 🔹 Step 5 — Meeting Time
            if chat_session.meeting_stage == "ask_time":
                meeting_time = user_message
                platform = chat_session.platform_selected
                chat_session.meeting_stage = None
                chat_session.save()

                # Create meeting link
                meeting_link = create_zoom_meeting() if platform == "Zoom" else "Google Meet link will be shared soon."

                # Email client
                send_mail(
                    subject=f"{platform} Meeting Scheduled with Bhaskar",
                    message=f"Hi {chat_session.name},\n\nYour {platform} meeting is confirmed.\nTime: {meeting_time}\nLink: {meeting_link}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[chat_session.email],
                    fail_silently=True
                )

                # Email owner (with extra details if provided)
                owner_msg = f"Client: {chat_session.name}\nEmail: {chat_session.email}\nTime: {meeting_time}\nPlatform: {platform}\nLink: {meeting_link}"
                if hasattr(chat_session, "extra_details"):
                    owner_msg += f"\nExtra Details: {chat_session.extra_details}"
                send_mail(
                    subject=f"New Meeting Scheduled ({platform})",
                    message=owner_msg,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True
                )

                return Response({"bot_reply": f"Your {platform} meeting is confirmed for {meeting_time}. Link: {meeting_link}"})

            # 🔹 Step 6 — AI Fallback
            reply = generate_smart_reply(user_message, chat_session.name, session_id=session_id)
            return Response({"bot_reply": reply})

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebugAPIView(APIView):
    def get(self, request):
        return Response({"status": "debug endpoint working"})
