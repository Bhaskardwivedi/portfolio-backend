# portfolio/chatwithus/test_google_meet.py

from datetime import datetime, timedelta
from portfolio.chatwithus.meeting_utils import create_google_meet, send_meeting_invitation_email

def main():
    # Meeting start & end time (10 min from now)
    start = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    print("🚀 Creating Google Meet...")
    print(f"📅 Start time: {start}")
    
    try:
        # Create the Google Meet
        meet_link = create_google_meet(
            start_time=start,
            topic="Chatbot Demo Meeting",
            description="Client discussion via chatbot",
            attendees=["bhaskardwivedi543@gmail.com"]  # test ke liye koi bhi email
        )

        print("✅ Google Meet link created:", meet_link)
        
        # Send custom email invitation
        print("📧 Sending custom email invitation...")
        email_sent = send_meeting_invitation_email(
            attendee_email="bhaskardwivedi543@gmail.com",
            meeting_link=meet_link,
            topic="Chatbot Demo Meeting",
            start_time=start,
            description="Client discussion via chatbot"
        )
        
        if email_sent:
            print("✅ Custom email invitation sent successfully!")
        else:
            print("❌ Failed to send custom email invitation")
            
    except Exception as e:
        print(f"❌ Error creating Google Meet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
