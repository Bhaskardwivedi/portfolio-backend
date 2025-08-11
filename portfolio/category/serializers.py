from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'type', 'use_icon', 'icon', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        img = getattr(obj, 'category_image', None)
        if img and hasattr(img, 'url'):
            url = img.url
            return request.build_absolute_uri(url) if request else url
        return None
