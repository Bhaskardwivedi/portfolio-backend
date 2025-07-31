from django.urls import path
from .views import SocialLinksAPIView 

urlpatterns = [ 
    path('', SocialLinksAPIView.as_view(), name='socials'),
]