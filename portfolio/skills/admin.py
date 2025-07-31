from django.contrib import admin 
from .models import Skill, SkillCategory
 
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'name', 'icon']

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name'] 