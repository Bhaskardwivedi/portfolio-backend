from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SocialLink
from .serializers import SocialLinkSerializer

class SocialLinksAPIView(APIView):
    def get(self, request):
        links = SocialLink.objects.filter(is_active=True)
        serializer = SocialLinkSerializer(links, many=True)
        return Response(serializer.data)
    
    