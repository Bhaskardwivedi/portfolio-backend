from django.urls import path 
from .views import ChatMessageAPIView, DebugAPIView
from .views_health import env_health, create_zoom_meeting



urlpatterns = [ 
    path('', ChatMessageAPIView.as_view(), name='chat-message-create'), 
   # path('feedback/', ChatFeedbackAPIView.as_view(), name='chat-feedback-create')
    path('debug/', DebugAPIView.as_view()),
    path('test_zoom/', env_health),
     path('create_zoom/', create_zoom_meeting),
]