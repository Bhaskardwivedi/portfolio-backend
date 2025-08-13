import json
import os
from datetime import datetime

LEARNINGS_FILE = os.path.join(os.path.dirname(__file__), "chatbot_learnings.json")

if not os.path.exists(LEARNINGS_FILE):
    with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"rules": []}, f, indent=2)

def load_learnings():
    with open(LEARNINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_learnings(data):
    with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def implicit_score(user_msg: str, bot_reply: str) -> float:
    
    positive_words = ["thanks", "great", "helpful", "yes", "ok", "sure"]
    negative_words = ["no", "not", "confused", "wrong", "bad", "later"]

    score = 0.5
    if any(w in user_msg.lower() for w in positive_words):
        score += 0.3
    if any(w in user_msg.lower() for w in negative_words):
        score -= 0.3

    return max(0, min(1, score))

def learn_from_conversation(user_msg: str, bot_reply: str):
    
    score = implicit_score(user_msg, bot_reply)
    data = load_learnings()

    if score < 0.4:  
        data["rules"].append({
            "avoid_text": bot_reply[:60],
            "created_at": datetime.utcnow().isoformat(),
            "reason": "Low implicit score",
        })
        save_learnings(data)

    return score
