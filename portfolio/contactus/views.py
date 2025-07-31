from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactMessageSerializer, ContactInfoSerializer
from .models import contactinfo
from rest_framework.generics import RetrieveAPIView

class ContactMessageCreateView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Custom formatted email message
            name = serializer.validated_data.get('name')
            email = serializer.validated_data.get('email')
            subject = serializer.validated_data.get('subject')
            message = serializer.validated_data.get('message')

            formatted_message = f"""
Hi Bhaskar,

You have received a new message from your portfolio website.

Name: {name}
Email: {email}
Message:
{message}

Regards,  
Your Portfolio form.
"""

            send_mail(
                subject=f"New Contact: {subject}",
                message=formatted_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['bhaskardwivedi544@gmail.com'],
                fail_silently=False,
            )

            return Response({'message': 'Sent successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactInfoView(APIView):
    def get(self, request):
        info = contactinfo.objects.first()
        serializer = ContactInfoSerializer(info)
        return Response(serializer.data)