from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AboutUs
from .serializers import AboutUsSerializer 
from .serializers import AboutUsHeroSerializer

class AboutUsView(RetrieveUpdateAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        return AboutUs.objects.first()
    
class AboutUsHeroAPIView(APIView):
    def get(self, request):
        about = AboutUs.objects.first()
        if not about:
            return Response({"error": "No AboutUs data found."}, status=404)
        serializer = AboutUsHeroSerializer(about)
        return Response(serializer.data)