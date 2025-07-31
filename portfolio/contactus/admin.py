from django.contrib import admin
from .models import contactMessage, contactinfo

@admin.register(contactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_filter = ['created_at']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']

@admin.register(contactinfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email', 'location', 'description']