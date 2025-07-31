import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage
)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# GPT-4 turbo instance
llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.6,
    openai_api_key=OPENAI_API_KEY
)

# ✅ Hardcoded profile intro for Bhaskar
def get_bhaskar_intro():
    return (
        "Bhaskar is a skilled Data Engineer and Analyst with 3+ years of experience. "
        "He builds robust data pipelines, automates web scraping, and creates insightful dashboards using Power BI. "
        "He also works with AI tools like LangChain and OpenAI to deliver intelligent automation solutions."
    )

# ✅ Smart reply generator function
def generate_smart_reply(user_input, user_name="Guest"):
    try:
        intro = get_bhaskar_intro()

        messages = [
            SystemMessage(content=
                f"You are Bhaskar's AI assistant.\n" 
                f"If the user's message is just 'hi', 'hello', or 'hey', then reply with a short and friendly message like: 'Hi! I'm Bhaskar's assistant. How can I help you today?'\n"
                f"Start by greeting the user politely and ask what help they need.\n" 
                f"If the user responds with a time (e.g., '12:30 PM'), assume it is for the previously discussed meeting. Do not ask again. Confirm the meeting and show the Google Meet link directly.\n"
                f"If they ask to schedule a meeting, confirm the time and show the meeting link.\n"
                f"Ask 1–2 clarifying questions about their project if needed.\n"
                f"BUT — if the user clearly says they want to work with Bhaskar or do business, then immediately suggest connecting over WhatsApp, Email, or a meeting.\n"
                f"If the user asks to connect with Bhaskar, don't ask more — just confirm and show connect options.\n"
                f"Only ask follow-up questions when the client is confused or unclear.\n"
                f"Never block or delay the connect if business intent is detected.\n"
                f"Keep responses short, polite, and professional. Avoid repeating questions.\n"
                f"If the user has already expressed interest in working with Bhaskar, do not repeat the same options.\n"
                f"Instead, move the conversation forward.\n"
                f"If they ask to schedule a meeting, confirm the time and show the meeting link.\n"
                f"If they say 'Email', ask only once, then give the email.\n"
                f"Avoid asking the same question again and again.\n"
            ),
            HumanMessage(content=user_input)
        ]

        response = llm(messages)
        return response.content

    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I couldn't generate a reply right now."

# ✅ Client need summarizer for lead email
def summarize_client_need(user_input):
    try:
        messages = [
            SystemMessage(content=
                "You are an intelligent assistant. Your job is to summarize the client's message into clear bullet points. "
                "Avoid repeating the message. Focus only on business needs. Make it short and structured."
            ),
            HumanMessage(content=user_input)        
        ]

        response = llm(messages)
        return response.content
    except Exception as e:
        print("Summary error:", e)
        return "Could not summarize client needs."
