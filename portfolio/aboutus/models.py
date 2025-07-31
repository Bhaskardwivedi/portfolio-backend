from django.db import models
import os
from django.utils.text import slugify
from datetime import date

def upload_to_profile(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"bhaskar.{ext}"  
    return os.path.join('about_images', filename) 

def upload_to_hero(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"bhaskardwivedi.{ext}"  
    return os.path.join('hero_images', filename)

class AboutUs(models.Model): 

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    headline = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    current_focus = models.CharField(max_length=255, blank=True, null=True)
    total_projects = models.PositiveIntegerField()
    total_clients = models.PositiveIntegerField()
    aboutus_image = models.ImageField(upload_to=upload_to_profile, blank=True, null=True) 
    hero_image = models.ImageField(upload_to=upload_to_hero, blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True) 

    @property
    def total_tech_experience(self):
        current_year = date.today().year
        return sum([
            (current_year - exp.start_year if exp.is_current else exp.total_years())
            for exp in self.experiences.filter(is_tech=True)
         ])
 
    def __str__(self):
        return self.name
    
class Experience(models.Model):

    about = models.ForeignKey('AboutUs', on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True) 
    is_current = models.BooleanField(default=False)
    is_tech = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
    
    def duration(self):
        if self.is_current:
            return f"{self.start_year} - Present"
        return f"{self.start_year} - {self.end_year}"
    
    def total_years(self):
        end = date.today().year if self.is_current else self.end_year
        return end - self.start_year if end and self.start_year else 0
    
    def get_total_it_experience(self):
        current_year = date.today().year
        return sum([
            (current_year - exp.start_year if exp.is_current else exp.total_years())
            for exp in self.experiences.filter(is_tech=True)
         ])

