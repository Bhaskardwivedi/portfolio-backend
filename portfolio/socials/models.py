from django.db import models

class SocialLink(models.Model): 

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
