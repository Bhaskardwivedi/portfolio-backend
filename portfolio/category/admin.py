from django.contrib import admin
from django.utils.html import format_html
from .models import Category

Category.verbose_name = "Categories"
Category.verbose_name_plural = "categories (services, projects)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'use_icon', 'type', 'image_thumb', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['type', 'use_icon']
    search_fields = ['name', 'slug', 'icon']

    def image_thumb(self, obj):
        img = getattr(obj, 'category_image', None)
        if img and hasattr(img, 'url'):
            return format_html(
                '<img src="{}" style="height:32px;border-radius:6px;" />',
                img.url
            )
        return "—"
    image_thumb.short_description = "Image"