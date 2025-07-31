from django.contrib import admin
from .models import Service, ServiceFeature
 
class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description', 'tagline']
    prepopulated_fields = {'slug': ('title',)} 

    inlines = [ServiceFeatureInline]