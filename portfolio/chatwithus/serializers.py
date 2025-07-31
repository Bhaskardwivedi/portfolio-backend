from rest_framework import serializers 
from .models import ChatMessage, ChatFeedback

class ChatMessageSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = ChatMessage
        fields = '__all__'

class ChatFeedbackSerializer(serializers.ModelSerializer): 
    class Meta:
        model = ChatFeedback
        fields = '__all__'
