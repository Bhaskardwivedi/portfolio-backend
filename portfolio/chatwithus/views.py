# chatwithus/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from datetime import datetime, timedelta
import urllib.parse
import os, json
import traceback

from .agent import generate_smart_reply, summarize_client_need
from .serializers import ChatFeedbackSerializer
from .zoom_utils import create_zoom_meeting
from textblob import TextBlob


class ChatMessageAPIView(APIView):
    conversation_memory = {}

    def analyze_user_message(self, message):
        """Analyze sentiment, urgency & intent from user message."""
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity
        urgency = "high" if any(x in message.lower() for x in ["urgent", "asap", "quick", "fast", "now"]) else "normal"
        intent = "repeat" if "already told" in message.lower() else "ask" if "?" in message else "inform"
        return {"sentiment": sentiment, "urgency": urgency, "intent": intent, "length": len(message.split())}

    def apply_learning_rules(self, reply, intent):
        """Apply RL-style fixes from chatbot_learnings.json."""
        try:
            path = os.path.join(os.getcwd(), "chatbot_learnings.json")
            with open(path, "r") as f:
                rules = json.load(f)
            for rule in rules:
                if rule["intent"] == intent and rule["bad_reply_contains"] in reply.lower():
                    return rule["replace_with"]
        except Exception as e:
            print("Learning rule error:", e)
        return reply

    def post(self, request):
        print("DEBUG: /api/chat/ POST request received")
        print("DEBUG request.data raw:", request.data)

        try:
            data = request.data
            if isinstance(data, list):
                print("DEBUG: data is a list, taking first element")
                if data and isinstance(data[0], dict):
                    data = data[0]
                else:
                    return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

            name = data.get("name", "Guest").strip()
            email = data.get("email", "").strip().lower()
            user_message = data.get("message", "").strip()

            print(f"DEBUG: Parsed name={name}, email={email}, message={user_message}")

            if not user_message or not email:
                print("ERROR: Missing email or message")
                return Response({"error": "Missing email or message"}, status=status.HTTP_400_BAD_REQUEST)

            misuse_keywords = ['what is', 'how to', 'generate code', 'explain', 'syntax', 'write a function']
            if any(word in user_message.lower() for word in misuse_keywords):
                print("DEBUG: Misuse query blocked")
                return Response({"bot_reply": "I'm Bhaskar's assistant. I help only with project discussions."})

            # Memory
            if email not in self.conversation_memory:
                self.conversation_memory[email] = {"stage": "ask_need", "need": None}
            memory = self.conversation_memory[email]
            print(f"DEBUG: Current memory={memory}")

            # NLP analysis
            behavior = self.analyze_user_message(user_message)
            print(f"DEBUG: NLP analysis={behavior}")

            # Stage-based conversation
            if memory["stage"] == "ask_need":
                if behavior["length"] >= 5 or any(k in user_message.lower() for k in ["dashboard", "need", "project"]):
                    memory["need"] = user_message
                    memory["stage"] = "confirm_meeting"
                    reply = "Thanks for sharing your requirement. Would you like to connect over WhatsApp or schedule a Zoom call?"
                elif user_message.lower() in ["hi", "hello", "hey", "good morning", "good evening"]:
                    reply = generate_smart_reply(user_message, name)
                else:
                    reply = "Could you please share what you'd like Bhaskar to help you with?"

            elif memory["stage"] == "confirm_meeting":
                if user_message.lower() in ["yes", "ok", "sure", "yep", "haan"]:
                    memory["stage"] = "booked"
                    reply = "Great! I'll book a Zoom meeting and notify Bhaskar. Please check your email shortly."
                else:
                    reply = "Would you prefer a Zoom call or connect over WhatsApp?"

            elif memory["stage"] == "booked":
                reply = "We've already scheduled a call. Bhaskar will reach out to you soon."

            reply = self.apply_learning_rules(reply, behavior["intent"])

            # Triggers
            trigger_contact = any(k in user_message.lower() for k in [
                'hire', 'freelance', 'project', 'work with you', 'build', 'website', 'develop'
            ])
            trigger_meeting = any(k in user_message.lower() for k in [
                'call', 'meet', 'schedule', 'talk', 'connect later', 'tomorrow', 'next week'
            ])
            is_meeting_time = any(k in user_message.lower() for k in ['am', 'pm', ':', 'at', 'noon', 'evening', 'morning'])

            zoom_meeting_link, calendar_link = None, None

            if trigger_meeting and is_meeting_time:
                try:
                    print("DEBUG: Auto-scheduling meeting...")
                    zoom_meeting_link = create_zoom_meeting()
                    start_time = datetime.utcnow() + timedelta(days=2)
                    end_time = start_time + timedelta(minutes=45)
                    calendar_link = (
                        "https://www.google.com/calendar/render?action=TEMPLATE"
                        f"&text=Zoom+Meeting+with+Bhaskar"
                        f"&dates={start_time.strftime('%Y%m%dT%H%M%SZ')}/{end_time.strftime('%Y%m%dT%H%M%SZ')}"
                        f"&details=Join+Zoom+Meeting:+{urllib.parse.quote(zoom_meeting_link)}"
                        f"&location=Zoom&trp=false"
                    )

                    send_mail(
                        subject=f"Zoom Meeting Scheduled with Bhaskar",
                        message=(
                            f"Hi {name},\n\nYour Zoom meeting with Bhaskar is confirmed.\n"
                            f"📅 Time: {user_message}\n"
                            f"🔗 Link: {zoom_meeting_link}\n"
                            f"📆 Add to Calendar: {calendar_link}\n\nBe ready on time.\n\nRegards,\nBhaskar's Assistant"
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        fail_silently=True
                    )

                    summary = summarize_client_need(memory.get("need", user_message))
                    send_mail(
                        subject=f"New Meeting Scheduled - {name}",
                        message=f"Client: {name}\nEmail: {email}\nNeed:\n{summary}\n\nMeeting Link: {zoom_meeting_link}",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True
                    )

                except Exception as e:
                    print("Meeting scheduling error:", e)
                    print(traceback.format_exc())

            if trigger_contact and not (trigger_meeting and is_meeting_time):
                try:
                    summary = summarize_client_need(user_message)
                    send_mail(
                        subject=f"New Client Lead via Chatbot - {name}",
                        message=f"Client: {name}\n\nNeed:\n{summary}\n\nFollow up soon.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True
                    )
                except Exception as e:
                    print("Lead email error:", e)
                    print(traceback.format_exc())

            return Response({
                "bot_reply": reply,
                "trigger_contact": trigger_contact,
                "trigger_meeting": trigger_meeting,
                "meeting_link": zoom_meeting_link,
                "calendar_link": calendar_link,
                "nlp_tags": behavior
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("ERROR in ChatMessageAPIView:", e)
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebugAPIView(APIView):
    def get(self, request):
        return Response({"message": "Debug view working fine!"}) 


def chat_view(request):
    try:
        print("DEBUG: /api/chat/ request reached")  
        return JsonResponse({"message": "Chat endpoint reached"}, status=200)
    except Exception as e:
        print("ERROR in /api/chat/:", e)
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
