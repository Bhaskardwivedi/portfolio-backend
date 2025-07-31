from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .agent import generate_smart_reply, summarize_client_need
from .serializers import ChatFeedbackSerializer
from django.core.mail import send_mail
from .zoom_utils import create_zoom_meeting
from datetime import datetime, timedelta
import urllib.parse
from textblob import TextBlob  
import os, json

# 🔁 Step 1: Store user conversation memory
class ChatMessageAPIView(APIView):
    conversation_memory = {}

    def analyze_user_message(self, message):
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity
        urgency = "high" if any(x in message.lower() for x in ["urgent", "asap", "quick", "fast", "now"]) else "normal"
        intent = "repeat" if "already told" in message.lower() else "ask" if "?" in message else "inform"
        return {
            "sentiment": sentiment,
            "urgency": urgency,
            "intent": intent,
            "length": len(message.split())
        }

    @staticmethod
    def apply_learning_rules(reply, intent):
        try:
            path = os.path.join(os.getcwd(), "chatbot_learnings.json")
            with open(path, "r") as f:
                rules = json.load(f)

            for rule in rules:
                if rule["intent"] == intent and rule["bad_reply_contains"] in reply.lower():
                    print(f"⚠️ Learned fix applied for intent={intent}")
                    return rule["replace_with"]
            return reply
        except Exception as e:
            print("Learning rule error:", e)
            return reply

    def post(self, request):
        try:
            name = request.data.get("name", "Guest")
            email = request.data.get("email")
            user_message = request.data.get("message")

            if not user_message or not email:
                return Response({"error": "Missing email or message"}, status=status.HTTP_400_BAD_REQUEST)

            misuse_keywords = ['what is', 'how to', 'generate code', 'explain', 'syntax', 'write a function']
            if any(word in user_message.lower() for word in misuse_keywords):
                return Response({
                    "bot_reply": "I'm Bhaskar's assistant. I help only with project discussions.",
                    "trigger_contact": False
                })

            if email not in self.conversation_memory:
                self.conversation_memory[email] = {"stage": "ask_need", "need": None}

            memory = self.conversation_memory[email]
            behavior = self.analyze_user_message(user_message)

            if memory["stage"] == "ask_need":
                if behavior["length"] >= 5 or "dashboard" in user_message.lower() or "need" in user_message.lower():
                    memory["need"] = user_message
                    memory["stage"] = "confirm_meeting"
                    reply = "Thanks for sharing your requirement. Would you like to connect over WhatsApp or schedule a Zoom call?"
                elif user_message.lower().strip() in ["hi", "hello", "hey", "good morning", "good evening"]:
                    reply = generate_smart_reply(user_message, name)
                else:
                    reply = "Could you please share what you'd like Bhaskar to help you with?"

            elif memory["stage"] == "confirm_meeting":
                casual_keywords = ["yes", "ok", "sure", "yep", "yess", "haan"]
                if user_message.lower() in casual_keywords:
                    memory["stage"] = "booked"
                    reply = "Great! I'll book a Zoom meeting and notify Bhaskar. Please check your email shortly."
                else:
                    reply = "Would you prefer a Zoom call or connect over WhatsApp?"

            elif memory["stage"] == "booked":
                reply = "We've already scheduled a call. Bhaskar will reach out to you soon."

            reply = self.apply_learning_rules(reply, behavior["intent"])

            business_keywords = ['hire', 'freelance', 'project', 'work with you', 'build', 'website', 'develop']
            trigger_contact = any(keyword in user_message.lower() for keyword in business_keywords)

            meeting_keywords = ['call', 'meet', 'schedule', 'talk', 'connect later', 'tomorrow', 'next week']
            time_keywords = ['am', 'pm', ':', 'at', 'noon', 'evening', 'morning']
            trigger_meeting = any(k in user_message.lower() for k in meeting_keywords)
            is_meeting_time = any(x in user_message.lower() for x in time_keywords)

            zoom_meeting_link = None
            calendar_link = None

            if trigger_meeting and is_meeting_time:
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

                recipients = [email, settings.EMAIL_HOST_USER]
                send_mail(
                    subject=f"Zoom Meeting Scheduled with Bhaskar",
                    message=(
                        f"Hi {name},\n\n"
                        f"Your Zoom meeting with Bhaskar is confirmed.\n"
                        f"📅 Time: {user_message}\n"
                        f"🔗 Link: {zoom_meeting_link}\n"
                        f"📆 Add to Calendar: {calendar_link}\n\n"
                        f"Be ready on time.\n\nRegards,\nBhaskar's Assistant"
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=recipients,
                    fail_silently=False
                )

            if trigger_contact:
                summary = summarize_client_need(user_message)
                send_mail(
                    subject=f"New Client Lead via Chatbot - {name}",
                    message=f"Client: {name}\n\nNeed:\n{summary}\n\nFollow up soon.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False
                )

            return Response({
                "bot_reply": reply,
                "trigger_contact": trigger_contact,
                "trigger_meeting": trigger_meeting,
                "meeting_link": zoom_meeting_link,
                "calendar_link": calendar_link,
                "nlp_tags": behavior
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ChatFeedbackAPIView(APIView): 
    def post(self, request):
        data = request.data.copy()

        if 'intent' not in data:
            analyzer = ChatMessageAPIView()
            behavior = analyzer.analyze_user_message(data.get("user_input", ""))
            data.update({
                "intent": behavior["intent"],
                "urgency": behavior["urgency"],
                "sentiment": behavior["sentiment"]
            })

        data["stage"] = data.get("stage", "unknown")

        serializer = ChatFeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
