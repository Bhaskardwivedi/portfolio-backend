from django.db import models

class SkillCategory(models.Model): 
    name = models.CharField(max_length=100) 

    def __str__(self): 
        return self.name
    
class Skill(models.Model):

    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name="skills") 
    name = models.CharField(max_length=100)
    proficiency = models.IntegerField(default=0)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0) 
    certificate_link = models.URLField(blank=True, null=True) 
    icon = models.ImageField(upload_to='skill_icons/', blank=True, null=True)

    def __str__(self):
        return self.name
    