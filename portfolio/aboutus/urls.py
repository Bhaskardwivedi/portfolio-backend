from django.urls import path
from .views import AboutUsView 
from .views import AboutUsHeroAPIView

urlpatterns = [ 
    path('', AboutUsView.as_view(), name='about_us'),
    path('home-hero/', AboutUsHeroAPIView.as_view(), name='about_us_hero'),
]