from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    use_icon = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True) 

    TYPE_CHOICES = (
        ('project', 'Project'),
        ('service', 'Service'),
        ('both', 'Both'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='project')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)    

    def __str__(self):
        return self.name
