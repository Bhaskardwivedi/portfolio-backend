from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer): 
    category_images = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'type', 'category_images', 'icon']

    def get_category_images(self, obj):
        request = self.context.get('request')
        if obj.category_images and hasattr(obj.category_images, 'url'):
            return request.build_absolute_uri(obj.category_images.url) if request else obj.category_images.url
        return None 
    
    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None 