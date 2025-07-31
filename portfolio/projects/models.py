from django.db import models
from django.utils.text import slugify
from portfolio.category.models import Category

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="projects")

    description = models.TextField()
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    demo_video = models.FileField(upload_to='project_videos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Project.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Feature(models.Model): 
    project = models.ForeignKey(Project, related_name='features', on_delete=models.CASCADE)
    text = models.CharField(max_length=400)

class TechStack(models.Model):
    project = models.ForeignKey(Project, related_name='tech_stacks', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='project_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='project_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.project.title}"