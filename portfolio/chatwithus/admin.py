from django.contrib import admin
from .models import ChatMessage 
from .models import ChatFeedback

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin): 
    list_display = ('name', 'email', 'created_at') 
    search_fields = ('name', 'email', 'message')

@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'feedback', 'created_at')
    search_fields = ('user_name', 'user_input', 'bot_reply')
