import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from portfolio.chatwithus.gmail_utils import send_email

def main():
    print("🚀 Starting email test...")
    
    to = "bhaskardwivedi544@gmail.com"   # apna email id
    subject = "✅ Test Email from Chatbot"
    body = "Hello Bhaskar,\n\nThis is a test email sent from your portfolio chatbot integration.\n\n- Chatbot"
    
    print(f"📧 Sending email to: {to}")
    print(f"📝 Subject: {subject}")
    
    try:
        result = send_email(to, subject, body)
        print("✅ Email sent successfully! Message ID:", result["id"])
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
