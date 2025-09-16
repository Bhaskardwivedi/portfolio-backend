import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# --- SCOPES ---
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.metadata",
    "https://www.googleapis.com/auth/userinfo.email"
]

# --- Credentials Loader ---
def get_gmail_service():
    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("gmail", "v1", credentials=creds)
    return service

# --- Mail Sender ---
def send_email(to, subject, body_text):
    service = get_gmail_service()

    # create MIME message
    message = MIMEText(body_text)
    message['to'] = to
    message['subject'] = subject

    # encode message
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {"raw": raw}

    # send mail
    send_result = service.users().messages().send(userId="me", body=message_body).execute()
    return send_result
