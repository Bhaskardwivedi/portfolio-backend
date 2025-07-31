# portfolio/contactus/urls.py

from django.urls import path
from .views import ContactMessageCreateView, ContactInfoView

urlpatterns = [
    path('', ContactMessageCreateView.as_view(), name='contact-submit'),
    path('contact-info/', ContactInfoView.as_view(), name='contact-info'),

]
