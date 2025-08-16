from django.db import models

class ChatMessage(models.Model): 
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
from django.db import models

class ChatFeedback(models.Model):
    user_name = models.CharField(max_length=100)
    user_input = models.TextField()
    bot_reply = models.TextField()
    feedback = models.CharField(max_length=10, choices=[('positive', '👍'), ('negative', '👎')])

    intent = models.CharField(max_length=20, blank=True, null=True)
    urgency = models.CharField(max_length=20, blank=True, null=True) 
    sentiment = models.FloatField(blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user_name} - {self.feedback} - {self.intent}"

class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    messages = models.JSONField(default=list)
    message_count = models.IntegerField(default=0)
    requirement_confirmed = models.BooleanField(default=False)
    last_intent = models.CharField(max_length=50, blank=True, null=True)
    meeting_stage = models.CharField(max_length=50, blank=True, null=True)
    platform_selected = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.session_id    