from django.contrib import admin
from .models import Project, Feature, TechStack, ProjectImage
 
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

class TechStackInline(admin.TabularInline):
    model = TechStack
    extra = 1    

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'order']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'description', 'tech_stack']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FeatureInline, TechStackInline, ProjectImageInline]