from django.urls import path 
from .views import ChatMessageAPIView, ChatFeedbackAPIView


urlpatterns = [ 
    path('', ChatMessageAPIView.as_view(), name='chat-message-create'), 
    path('feedback/', ChatFeedbackAPIView.as_view(), name='chat-feedback-create')
    
]