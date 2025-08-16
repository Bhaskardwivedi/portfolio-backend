from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service
from .serializers import ServiceSerializer

class ServiceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ServiceSerializer 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug']

class ServiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer 
    lookup_field = "slug"
    
    
        

