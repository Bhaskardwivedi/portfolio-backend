from django.urls import path 
from .views import ChatMessageAPIView, DebugAPIView
from .views_health import env_health



urlpatterns = [ 
    path('', ChatMessageAPIView.as_view(), name='chat-message-create'), 
   # path('feedback/', ChatFeedbackAPIView.as_view(), name='chat-feedback-create')
    path('debug/', DebugAPIView.as_view()),
    path('health/', env_health),
]