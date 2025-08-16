import json
import os
from datetime import datetime
from typing import Dict, Any, List

# -------------------- FILE SETUP --------------------
LEARNINGS_FILE = os.path.join(os.path.dirname(__file__), "chatbot_learnings.json")

# Ensure file exists
if not os.path.exists(LEARNINGS_FILE):
    with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"rules": []}, f, indent=2, ensure_ascii=False)


# -------------------- LOAD & SAVE --------------------
def load_learnings() -> Dict[str, Any]:
    """Load chatbot learnings from file."""
    try:
        with open(LEARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"rules": []}
    except Exception as e:
        print(f"[ERROR] Failed to load learnings: {e}")
        return {"rules": []}


def save_learnings(data: Dict[str, Any]) -> None:
    """Save chatbot learnings to file."""
    try:
        with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save learnings: {e}")


# -------------------- SCORING LOGIC --------------------
POSITIVE_WORDS = ["thanks", "great", "helpful", "yes", "ok", "sure", "perfect", "good", "amazing", "love"]
NEGATIVE_WORDS = ["no", "not", "confused", "wrong", "bad", "later", "boring", "hate", "useless"]

def implicit_score(user_msg: str, bot_reply: str) -> float:
    """
    Score the conversation implicitly based on positive/negative keywords.
    Score range: 0 (very bad) → 1 (excellent)
    """
    score = 0.5
    user_lower = user_msg.lower()

    if any(w in user_lower for w in POSITIVE_WORDS):
        score += 0.3
    if any(w in user_lower for w in NEGATIVE_WORDS):
        score -= 0.3

    # Bonus if bot reply matches user tone (positive → positive)
    if score >= 0.8 and "?" not in bot_reply:
        score += 0.1  # direct helpful answer

    return max(0, min(1, round(score, 2)))


# -------------------- LEARNING UPDATE --------------------
def learn_from_conversation(user_msg: str, bot_reply: str) -> float:
    """
    Learn from user feedback or conversation tone.
    If score is low, save a rule to avoid similar replies in future.
    """
    score = implicit_score(user_msg, bot_reply)
    data = load_learnings()

    if score < 0.4:
        new_rule = {
            "avoid_text": bot_reply.strip()[:80],  # Store first 80 chars for better match
            "created_at": datetime.utcnow().isoformat(),
            "reason": "Low implicit score",
            "user_message": user_msg.strip(),
            "score": score
        }

        # Avoid adding duplicate rules
        if not any(rule["avoid_text"] == new_rule["avoid_text"] for rule in data["rules"]):
            data["rules"].append(new_rule)
            save_learnings(data)
            print(f"[LEARNING] Rule added for low-score reply: {new_rule['avoid_text']}")

    return score
