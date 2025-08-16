from __future__ import annotations
import os, json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .evaluator import learn_from_conversation, load_learnings

# Django ORM import for persistent memory
from portfolio.chatwithus.models import ChatSession  

load_dotenv()

# Global memory for feedback storage
_MEMORY: Dict[str, List[Dict[str, Any]]] = {}

# -------------------- LLM SETUP --------------------
def _make_llm():
    try:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.4, timeout=20)
    except Exception as e:
        print("LLM init error:", type(e).__name__, e)
        return None

LLM = _make_llm()

# -------------------- PROFILE FETCH --------------------
def _fetch_from_models() -> Optional[Dict[str, Any]]:
    try:
        from portfolio.aboutus.models import AboutUs
        from portfolio.skills.models import Skill
        from portfolio.projects.models import Project
        from portfolio.services.models import Service as ServiceModel

        about = AboutUs.objects.first()
        intro = ""

        if about:
            intro = " | ".join([
                getattr(about, "name", "") or "",
                getattr(about, "title", "") or "",
                getattr(about, "description", "") or ""
            ]).strip(" | ")
        skills = list(Skill.objects.values_list("name", flat=True))
        projects = []

        for p in Project.objects.prefetch_related("tech_stacks", "features").all()[0:5]:
            projects.append({
                "title": p.title.strip(),
                "tagline": (p.tagline or "").strip(),
                "description": (p.description or "").strip(),
                "tech_stacks": list(p.tech_stacks.values_list("name", flat=True)),
                "features": list(p.features.values_list("point", flat=True)),
            })
       
        services = []
        for s in ServiceModel.objects.filter(is_active=True).values("title", "description"):
            services.append({
                "title": (s.get("title") or "").strip(),
                "description": (s.get("description") or "").strip(),
            })

        return {"intro": intro,
                "skills": skills,
                "projects": projects, 
                "services": services
                } if (intro or skills or projects or services) else None
    
    except Exception as e:
        print("Profile fetch error:", e)
        return None

def fetch_from_json(path: str = "chatbot_knowledge.json") -> Optional[Dict[str, Any]]:
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception as e:
        print("JSON fetch error:", e)
        return None

def _defaults() -> Dict[str, Any]:
    return {
        "intro": "Bhaskar is a Data Engineer, Automation Expert & Web Developer...",
        "skills": ["Python", "SQL", "Power BI", "Django", "React", "LangChain", "OpenAI", "Azure Data Factory"],
        "projects": [
            {"title": "AI Job Recommender", "description": "Scrapes JDs, ranks matches, assists apply.", "tech_stack": "Python, LangChain, OpenAI", "link": ""},
            {"title": "B2B Portal Automation", "description": "Role-based portal with recharge API.", "tech_stack": "Django, React, Postgres", "link": ""},
        ],
        "services": []
    }

def get_profile() -> Dict[str, Any]:
    return _fetch_from_models() or fetch_from_json() or _defaults()

# -------------------- FORMAT HELPERS --------------------
def _fmt_skills(skills: List[str], limit=12) -> str:
    return ", ".join([s for s in skills if s][:limit]) or "(skills not listed)"

def _fmt_projects(projects: List[Dict[str, Any]], limit=3) -> str:
    out = []
    for p in projects[:limit]:
        line = f"- {p.get('title', '')}: {p.get('description', '')}"
        if p.get("tech_stacks"):
            line += f" [{', '.join(p['tech_stacks'])}]"
        if p.get("link"):
            line += f" ({p['link']})"
        out.append(line)
    return "\n".join(out) if out else "(no projects yet)"

# -------------------- PERSISTENT MEMORY --------------------
def get_session_context(session_id: str, max_chars=900) -> str:
    try:
        session = ChatSession.objects.filter(session_id=session_id).first()
        if session:
            return "\n".join(session.messages)[-max_chars:]
    except Exception as e:
        print("Session fetch error:", e)
    return ""

def push_memory(session_id: str, user_line: str, bot_line: str):
    try:
        session, created = ChatSession.objects.get_or_create( 
            session_id=session_id, 
            defaults={"messages": []}
        )
        msgs = session.messages or []
        if not isinstance(msgs, list):
            msgs = []

        msgs.extend([user_line, bot_line])
        session.messages = msgs
        session.save()
    except Exception as e:
        print("Session save error:", e)

# -------------------- SYSTEM PROMPTS --------------------
SYSTEM = (
    "You are Bhaskar’s assistant. Be concise (≤2 lines), friendly, accurate.\n"
    "Use PROFILE faithfully. If unsure, ask ONE clarifying question.\n"
    "If business intent is clear (hire/work/meet/call), suggest ONE connect option using intro for personalization.\n"
    "Avoid repeating the same options in consecutive replies."
)

CRITIC = (
    "Review DRAFT vs PROFILE & USER need. If issues (wrong/vague/repetitive), reply 'FIX_NEEDED: <hint>'. Else 'OK'."
)

# -------------------- MAIN REPLY GENERATOR --------------------
def generate_smart_reply(user_input: str, user_name="GUEST", session_id="anon") -> str:
    data = get_profile()
    profile_ctx = f"INTRO:\n{data['intro']}\n\nSKILLS:\n{_fmt_skills(data['skills'])}\n\nPROJECTS:\n{_fmt_projects(data['projects'])}\n"
    ctx = get_session_context(session_id)
    lower_inp = user_input.lower()

    # ---- 1. Quick intent detection ----
    meeting_keywords = ["meet", "call", "connect", "zoom", "schedule"]
    project_keywords = ["project", "build", "develop", "automation", "website", "app"]
    
    if any(k in lower_inp for k in meeting_keywords):
        intro_line = data['intro'].split("\n")[0] if data.get('intro') else "I'm Bhaskar’s assistant."
        return attach_feedback(
            f"{intro_line} We can set up a quick meeting — would you prefer Zoom or Google Meet?",
            session_id, user_input
        )

    # ---- 2. Auto project showcase if project-related ----
    if any(k in lower_inp for k in project_keywords):
        showcase = suggest_relevant_projects(lower_inp, data['projects'])
        follow_up_q = "Could you share more about your requirements so we can tailor it exactly for you?"
        return attach_feedback(f"{showcase} {follow_up_q}", session_id, user_input)

    # ---- 3. LLM draft ----
    if LLM is None:
        return attach_feedback(_fallback(user_input, data), session_id, user_input)

    draft = LLM.invoke([
        SystemMessage(content=f"{SYSTEM}\n\nPROFILE:\n{profile_ctx}"),
        HumanMessage(content=f"CONTEXT:\n{ctx or '(none)'}\n\nUSER({user_name}): {user_input.strip()}")
    ]).content.strip()

    # ---- 4. Critic check ----
    verdict = LLM.invoke([
        SystemMessage(content=f"{CRITIC}\n\nPROFILE FOR CHECK:\n{profile_ctx}"),
        HumanMessage(content=f"USER: {user_input}\n\nDRAFT: {draft}")
    ]).content.strip()

    final = draft
    if verdict.startswith("FIX_NEEDED"):
        final = LLM.invoke([
            SystemMessage(content=f"{SYSTEM}\n\nPROFILE:\n{profile_ctx}"),
            HumanMessage(content=f"Refine per critic. Keep ≤2 lines.\nDRAFT:\n{draft}\nCRITIC:\n{verdict}")
        ]).content.strip()

    # ---- 5. Apply learnings from JSON ----
    rules = load_learnings().get("rules", [])
    for r in rules:
        if r.get("avoid_text") and r["avoid_text"].lower() in final.lower():
            final = final.replace(r["avoid_text"], "").strip()

    # ---- 6. Save learning & memory ----
    learn_from_conversation(user_input, final)
    push_memory(session_id, user_input, final)

    return attach_feedback(final, session_id, user_input)


# --- Helper to save pending feedback ---
def save_pending_feedback(session_id, user_input, reply_text):
    """Save feedback data for later processing"""
    try:
        # Store in session memory for now
        if session_id not in _MEMORY:
            _MEMORY[session_id] = []
        _MEMORY[session_id].append({
            "user_input": user_input,
            "reply_text": reply_text,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Feedback save error: {e}")

# --- Helper to attach 👍 / 👎 buttons ---
def attach_feedback(reply_text, session_id, user_input):
    save_pending_feedback(session_id, user_input, reply_text)
    return f"{reply_text}\n\n[👍] [👎]"

# --- Suggest relevant projects ---
def suggest_relevant_projects(user_message, all_projects):
    # Very simple keyword match for now
    for proj in all_projects:
        if any(k.lower() in proj['title'].lower() for k in user_message.split()):
            return f"We’ve built a similar project: {proj['title']} — {proj['tagline']}"
    return "We’ve delivered multiple successful projects in this domain."

# -------------------- FALLBACK --------------------
def _fallback(user_input: str, data: Dict[str, Any]) -> str:
    u = (user_input or "").lower().strip()
    if any(g in u for g in ["hi", "hello", "hey", "namaste"]) and len(u) <= 12:
        return "Hi! I’m Bhaskar’s assistant. How can I help you today?"
    if "project" in u or "portfolio" in u:
        return _fmt_projects(data.get("projects", []), limit=1)
    if "skill" in u or "stack" in u:
        return f"Key skills: {_fmt_skills(data.get('skills', []))}."
    if "about" in u or "intro" in u:
        intro = data.get("intro", "")
        return intro[:200] + ("..." if len(intro) > 200 else "")
    return "Got it—could you share a bit more so I can be specific?"

# -------------------- CLIENT NEED SUMMARIZER --------------------
def summarize_client_need(user_input: str, session_id: str = "anon") -> str:
    """
    Summarizes the client's requirement into bullet points for mailing or CRM.
    Uses LLM if available, else falls back to a simple format.
    """
    ctx = get_session_context(session_id)

    if LLM is None:
        return f"- {user_input.strip()}"

    prompt = (
        "Summarize the client's needs into 3-5 short bullet points. "
        "Be specific, remove filler text, and focus on actionable requirements."
    )

    return LLM.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Conversation so far:\n{ctx}\n\nLatest input:\n{user_input.strip()}")
    ]).content.strip()