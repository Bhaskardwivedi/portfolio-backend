import json
from portfolio.chatwithus.models import ChatFeedback

def generate_learning_rules():
    bad_feedbacks = ChatFeedback.objects.filter(feedback="negative")

    rules = []
    seen = set()

    for feedback in bad_feedbacks:
        intent = feedback.intent or "unknown"
        reply = feedback.bot_reply.lower()

        for word in reply.split():
            if len(word) >= 4 and word in reply:
                rule_key = (intent, word)
                if rule_key not in seen:
                    seen.add(rule_key)
                    rules.append({
                        "intent": intent,
                        "bad_reply_contains": word,
                        "replace_with": f"(You decide): Better reply for intent={intent} when bot says '{word}'"
                    })

    with open("chatbot_learnings.json", "w") as f:
        json.dump(rules, f, indent=2)
        print("✅ Learning rules saved to chatbot_learnings.json")

