from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    use_icon = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    category_image = CloudinaryField('category_images', blank=True, null=True) 
    class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "categories (services, projects)"
        
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
