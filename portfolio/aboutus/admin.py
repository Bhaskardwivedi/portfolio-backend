from django.contrib import admin
from .models import AboutUs, Experience, Skill
 
class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1 

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_tech_experience', 'total_projects', 'total_clients', 'updated_at')
    readonly_fields = ('updated_at',)
    inlines = [ExperienceInline, SkillInline] 


