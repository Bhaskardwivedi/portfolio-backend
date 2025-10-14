from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def _gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def _create_message(sender: str, to: str, subject: str, html_body: str):
    msg = MIMEText(html_body, "html")
    msg["to"] = to
    msg["from"] = sender
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}

def send_invite_email(sender_email: str, to_email: str, subject: str,
                      join_url: str, calendar_link: str | None,
                      start_ist_iso: str):
    """
    Send an HTML invite email with Zoom link (+ optional calendar link).
    """
    html = f"""
    <div>
      <p>Hi,</p>
      <p>Your meeting is scheduled.</p>
      <p><b>Start (IST):</b> {start_ist_iso}</p>
      <p><b>Zoom:</b> <a href="{join_url}">{join_url}</a></p>
      {"<p><b>Calendar:</b> <a href='" + calendar_link + "'>View in Google Calendar</a></p>" if calendar_link else ""}
      <p>Regards,<br/>Assistant</p>
    </div>
    """
    service = _gmail_service()
    message = _create_message(sender_email, to_email, subject, html)
    sent = service.users().messages().send(userId="me", body=message).execute()
    return {"message_id": sent.get("id")}
