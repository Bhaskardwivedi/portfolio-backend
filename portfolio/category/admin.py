from django.contrib import admin
from .models import Category

Category.verbose_name = "Categories"
Category.verbose_name_plural = "categories (services, projects)"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'use_icon', 'category_images', 'type', 'icon']
    prepopulated_fields = {'slug': ('name',)}
