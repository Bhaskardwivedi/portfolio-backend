from portfolio.chatwithus import gmail_utils

if __name__ == "__main__":
    out = gmail_utils.send_invite_email(
        sender_email="assistant@bhaskarai.com",
        to_email="bhaskardwivedi544@gmail.com",
        subject="Test: Bhaskar.AI Gmail API",
        join_url="https://zoom.us/j/123456789",
        calendar_link=None,
        start_ist_iso="2025-10-13T16:00:00+05:30"
    )
    print(out)
