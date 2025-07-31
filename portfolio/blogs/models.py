from django.db import models 
from django.utils.text import slugify

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField() 
    image = models.ImageField(upload_to='blogs/')
    slug = models.SlugField(unique=True, null=False, blank=False, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 
    is_published = models.BooleanField(default=True)
    

    def save(self, *args, **kwargs): 
        if not self.slug: 
            self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.blog.title}"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
        return f"{self.email}"
    