from django.contrib import admin
from .models import Blog, Comment, Subscriber

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'image', 'created_at') 
    prepopulated_fields = {'slug': ('title',)} 

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'name', 'email', 'created_at')
    list_filter = ('blog', 'created_at')
    search_fields = ('name', 'email', 'content') 

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at') 
    search_fields = ('email',)

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)

