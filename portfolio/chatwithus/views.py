from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache

from .agent import generate_smart_reply, summarize_client_need
from .serializers import ChatFeedbackSerializer
from .zoom_utils import create_zoom_meeting

from datetime import datetime, timedelta
import urllib.parse
import os
import json
import logging
import dateparser
import pytz
from textblob import TextBlob

logger = logging.getLogger(__name__)

# ---- Learning rules: load once at import time (faster & stable path) ----
RULES_PATH = os.path.join(settings.BASE_DIR, "portfolio", "chatwithus", "chatbot_learnings.json")
try:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        LEARNING_RULES = json.load(f) or []
except Exception as e:
    logger.warning("Could not load learning rules: %s", e)
    LEARNING_RULES = []


class ChatMessageAPIView(APIView):
    """Main chat endpoint: analyzes message, keeps lightweight memory, suggests meeting, emails summary."""

    # ------ Lightweight analyzers ------
    def analyze_user_message(self, message: str):
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity
        urgency = "high" if any(x in message.lower() for x in ["urgent", "asap", "quick", "fast", "now"]) else "normal"
        intent = "repeat" if "already told" in message.lower() else ("ask" if "?" in message else "inform")
        return {
            "sentiment": sentiment,
            "urgency": urgency,
            "intent": intent,
            "length": len(message.split()),
        }

    @staticmethod
    def apply_learning_rules(reply: str, intent: str | None):
        try:
            text = (reply or "").lower()
            for rule in LEARNING_RULES:
                rule_intent = rule.get("intent")
                if rule_intent and rule_intent != intent:
                    continue
                bads = rule.get("bad_reply_contains", [])
                if isinstance(bads, str):
                    bads = [bads]
                if any((b or "").lower() in text for b in bads):
                    replacement = rule.get("replace_with")
                    if replacement:
                        logger.info("\u26a0\ufe0f Learned fix applied (intent=%s)", intent)
                        return replacement
            return reply
        except Exception:
            logger.exception("Learning rule error")
            return reply

    # ------ Helpers ------
    @staticmethod
    def _get_memory(email: str):
        key = f"conv:{email}"
        return cache.get(key) or {"stage": "ask_need", "need": None}

    @staticmethod
    def _set_memory(email: str, memory: dict):
        key = f"conv:{email}"
        cache.set(key, memory, timeout=60 * 60 * 24)  # 24h

    @staticmethod
    def _parse_meeting_time(text: str):
        """Parse natural time like 'tomorrow 4 pm' in Asia/Kolkata. Fallback to +2 days 12:30."""
        tz = pytz.timezone("Asia/Kolkata")
        dt_local = dateparser.parse(
            text,
            settings={"TIMEZONE": "Asia/Kolkata", "RETURN_AS_TIMEZONE_AWARE": False, "PREFER_DATES_FROM": "future"},
        )
        if dt_local is None:
            dt_local = datetime.now() + timedelta(days=2)
            dt_local = dt_local.replace(hour=12, minute=30, second=0, microsecond=0)
        start_local = tz.localize(dt_local)
        end_local = start_local + timedelta(minutes=45)
        return start_local, end_local

    def post(self, request):
        try:
            name = request.data.get("name", "Guest")
            email = request.data.get("email")
            user_message = request.data.get("message", "")

            if not user_message or not email:
                return Response({"error": "Missing email or message"}, status=status.HTTP_400_BAD_REQUEST)

            # softer guard (allow short query but nudge to business)
            BUSINESS_HINTS = [
                "hire", "project", "work with you", "build", "website", "develop", "dashboard", "automation", "data", "ml", "meeting", "call", "quote", "estimate",
            ]
            is_business = any(k in user_message.lower() for k in BUSINESS_HINTS)
            if not is_business and len(user_message.split()) < 3:
                return Response({
                    "bot_reply": "I'm Bhaskar's assistant for project discussions. Thodi requirement batao—industry, kya banana hai, deadline?",
                    "trigger_contact": False,
                })

            # get/update memory from cache
            memory = self._get_memory(email)
            behavior = self.analyze_user_message(user_message)

            # ---- Conversation policy ----
            if memory["stage"] == "ask_need":
                if behavior["length"] >= 5 or any(k in user_message.lower() for k in ["dashboard", "need", "website", "automation", "pipeline", "ml"]):
                    memory["need"] = user_message
                    memory["stage"] = "confirm_meeting"
                    reply = "Thanks for sharing. Shall I book a quick Zoom or share WhatsApp/email to connect?"
                elif user_message.lower().strip() in ["hi", "hello", "hey", "good morning", "good evening"]:
                    reply = generate_smart_reply(user_message, name)
                else:
                    reply = "Kis cheez me help chahiye—website, data engineering, ML ya automation?"

            elif memory["stage"] == "confirm_meeting":
                casual_keywords = ["yes", "ok", "sure", "yep", "yess", "haan", "book", "schedule"]
                if user_message.lower() in casual_keywords:
                    memory["stage"] = "booked"
                    reply = "Great! Time likh do (e.g., tomorrow 4 pm IST) — main link bhej deta hoon."
                else:
                    reply = "Prefer Zoom or WhatsApp? Agar Zoom, to apna preferred time bata do."

            elif memory["stage"] == "booked":
                reply = "Meeting process started. Time confirm karte hi link share karunga."

            else:
                reply = generate_smart_reply(user_message, name)

            reply = self.apply_learning_rules(reply, behavior["intent"])  # RL pass

            # ---- Triggers ----
            business_keywords = ["hire", "freelance", "project", "work with you", "build", "website", "develop"]
            trigger_contact = any(keyword in user_message.lower() for keyword in business_keywords)

            meeting_keywords = ["call", "meet", "schedule", "talk", "connect later", "tomorrow", "next week", "pm", "am"]
            trigger_meeting = any(k in user_message.lower() for k in meeting_keywords)

            zoom_meeting_link = None
            calendar_link = None

            # if user typed a time, try to schedule coherently
            if trigger_meeting:
                start_local, end_local = self._parse_meeting_time(user_message)
                start_iso_local = start_local.strftime('%Y-%m-%dT%H:%M:%S')

                # create Zoom at same time (Asia/Kolkata)
                zoom_meeting_link = create_zoom_meeting(start_time=start_iso_local)

                start_utc = start_local.astimezone(pytz.utc)
                end_utc = end_local.astimezone(pytz.utc)
                calendar_link = (
                    "https://www.google.com/calendar/render?action=TEMPLATE"
                    f"&text=Zoom+Meeting+with+Bhaskar"
                    f"&dates={start_utc.strftime('%Y%m%dT%H%M%SZ')}/{end_utc.strftime('%Y%m%dT%H%M%SZ')}"
                    f"&details=Join+Zoom+Meeting:+{urllib.parse.quote(zoom_meeting_link or '')}"
                    f"&location=Zoom&trp=false"
                )

                # notify both
                recipients = [email, settings.EMAIL_HOST_USER]
                try:
                    send_mail(
                        subject="Zoom Meeting Scheduled with Bhaskar",
                        message=(
                            f"Hi {name},\n\n"
                            f"Your Zoom meeting with Bhaskar is planned.\n"
                            f"\ud83d\udcc5 Time (IST): {start_local.strftime('%a %d %b, %I:%M %p')}\n"
                            f"\ud83d\udd17 Link: {zoom_meeting_link}\n"
                            f"\ud83d\udcc6 Add to Calendar: {calendar_link}\n\n"
                            f"Regards,\nBhaskar's Assistant"
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=recipients,
                        fail_silently=False,
                    )
                except Exception:
                    logger.exception("Email send failed for meeting notify")

            # lead summary to owner when business intent detected
            if trigger_contact:
                try:
                    summary = summarize_client_need(user_message)
                    send_mail(
                        subject=f"New Client Lead via Chatbot - {name}",
                        message=f"Client: {name}\n\nNeed:\n{summary}\n\nFollow up soon.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=False,
                    )
                except Exception:
                    logger.exception("Lead email send failed")

            # persist memory
            self._set_memory(email, memory)

            return Response(
                {
                    "bot_reply": reply,
                    "trigger_contact": trigger_contact,
                    "trigger_meeting": trigger_meeting,
                    "meeting_link": zoom_meeting_link,
                    "calendar_link": calendar_link,
                    "nlp_tags": behavior,
                },
                status=200,
            )

        except Exception as e:
            logger.exception("ChatMessageAPIView error: %s", e)
            return Response({"error": str(e)}, status=500)


class ChatFeedbackAPIView(APIView):
    def post(self, request):
        data = request.data.copy()

        if "intent" not in data:
            analyzer = ChatMessageAPIView()
            behavior = analyzer.analyze_user_message(data.get("user_input", ""))
            data.update(
                {
                    "intent": behavior["intent"],
                    "urgency": behavior["urgency"],
                    "sentiment": behavior["sentiment"],
                }
            )

        data["stage"] = data.get("stage", "unknown")

        serializer = ChatFeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
