from django.db import models

class contactMessage(models.Model): 
    name = models.CharField(max_length=100) 
    email = models.EmailField() 
    subject = models.CharField(max_length=200) 
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class contactinfo(models.Model):
    description = models.TextField()
    phone=models.CharField(max_length=200)
    email=models.EmailField()
    location=models.CharField(max_length=255)
    
    def __str__(self):
        return "contact info"
    