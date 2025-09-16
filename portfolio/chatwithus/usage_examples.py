"""
Usage examples for Zoom + Google Calendar integration in Django
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .zoom_utils import create_zoom_meeting
from .calendar_utils import create_calendar_event, send_meeting_invite
from django.shortcuts import render # Added missing import
from django.core.mail import send_mail # Added missing import

# Example 1: Simple API endpoint to create meeting with calendar
@csrf_exempt
@require_http_methods(["POST"])
def create_meeting_api(request):
    """API endpoint to create Zoom meeting with calendar event"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', 'Client Meeting with Bhaskar')
        start_time = data.get('start_time')  # ISO string or None
        attendee_emails = data.get('attendee_emails', [])
        create_calendar = data.get('create_calendar', True)
        
        result = create_zoom_meeting(
            topic=topic,
            start_time=start_time,
            create_calendar_event=create_calendar,
            attendee_emails=attendee_emails if attendee_emails else None
        )
        
        if result:
            return JsonResponse({
                'success': True,
                'meeting': result['zoom'],
                'calendar': result['calendar']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create meeting'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Example 2: Django view for meeting creation form
def create_meeting_view(request):
    """Django view for meeting creation form"""
    if request.method == 'POST':
        topic = request.POST.get('topic')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        attendee_emails = request.POST.get('attendee_emails', '').split(',')
        attendee_emails = [email.strip() for email in attendee_emails if email.strip()]
        
        # Combine date and time
        if start_date and start_time:
            from datetime import datetime
            start_datetime = f"{start_date}T{start_time}:00"
        else:
            start_datetime = None
        
        result = create_zoom_meeting(
            topic=topic,
            start_time=start_datetime,
            create_calendar_event=True,
            attendee_emails=attendee_emails if attendee_emails else None
        )
        
        if result:
            # Redirect to success page or show success message
            context = {
                'meeting': result['zoom'],
                'calendar': result['calendar']
            }
            return render(request, 'meeting_success.html', context)
        else:
            # Show error message
            context = {'error': 'Failed to create meeting'}
            return render(request, 'meeting_form.html', context)
    
    # GET request - show form
    return render(request, 'meeting_form.html')

# Example 3: Function to create meeting from chat/contact form
def create_meeting_from_contact(contact_data):
    """
    Create meeting when someone contacts through your website
    
    Args:
        contact_data: Dict with name, email, message, preferred_time, etc.
    """
    try:
        # Extract meeting details from contact form
        topic = f"Consultation with {contact_data.get('name', 'Client')}"
        
        # Parse preferred time if provided
        start_time = None
        if contact_data.get('preferred_time'):
            from datetime import datetime
            try:
                start_time = datetime.fromisoformat(contact_data['preferred_time'])
            except:
                pass  # Use default time if parsing fails
        
        # Create meeting
        result = create_zoom_meeting(
            topic=topic,
            start_time=start_time,
            create_calendar_event=True,
            attendee_emails=[contact_data.get('email')] if contact_data.get('email') else None
        )
        
        if result:
            # Send confirmation email to client
            send_confirmation_email(
                to_email=contact_data.get('email'),
                meeting_details=result['zoom'],
                calendar_link=result['calendar']['html_link'] if result['calendar'] else None
            )
            
            return {
                'success': True,
                'meeting_id': result['zoom']['meeting_id'],
                'join_url': result['zoom']['join_url']
            }
        else:
            return {'success': False, 'error': 'Failed to create meeting'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Example 4: Scheduled meeting creation (for recurring meetings)
def create_recurring_meetings():
    """Create recurring meetings (e.g., weekly team sync)"""
    from datetime import datetime, timezone, timedelta
    
    # Create meetings for next 4 weeks
    for week in range(4):
        meeting_time = datetime.now(timezone.utc) + timedelta(weeks=week+1, hours=10)  # 10 AM
        
        result = create_zoom_meeting(
            topic="Weekly Team Sync",
            start_time=meeting_time.isoformat(),
            create_calendar_event=True,
            attendee_emails=["team@company.com", "manager@company.com"]
        )
        
        if result:
            print(f"✅ Created recurring meeting for week {week+1}")
        else:
            print(f"❌ Failed to create recurring meeting for week {week+1}")

# Example 5: Integration with existing Django models
def create_meeting_from_project(project):
    """Create meeting based on project data"""
    try:
        topic = f"Project Discussion: {project.title}"
        
        # Set meeting time to tomorrow at 2 PM
        from datetime import datetime, timezone, timedelta
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1, hours=14)
        
        result = create_zoom_meeting(
            topic=topic,
            start_time=tomorrow.isoformat(),
            create_calendar_event=True,
            attendee_emails=[project.client_email] if hasattr(project, 'client_email') else None
        )
        
        if result:
            # Update project with meeting details
            project.zoom_meeting_id = result['zoom']['meeting_id']
            project.zoom_join_url = result['zoom']['join_url']
            project.calendar_event_id = result['calendar']['event_id'] if result['calendar'] else None
            project.save()
            
            return result
        else:
            return None
            
    except Exception as e:
        print(f"Error creating meeting from project: {e}")
        return None
