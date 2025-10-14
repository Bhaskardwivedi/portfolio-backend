# test_calendar_quick.py
from portfolio.chatwithus.calendar_utils import create_calendar_event

if __name__ == "__main__":
    res = create_calendar_event(
        topic="Calendar Test via Bhaskar.AI",
        start_iso_ist="2025-10-13T19:30:00+05:30",
        duration_min=30,
        attendee_email=None,
        join_url="https://zoom.us/j/123456789"
    )
    print(res)
