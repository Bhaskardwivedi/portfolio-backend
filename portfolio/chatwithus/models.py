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