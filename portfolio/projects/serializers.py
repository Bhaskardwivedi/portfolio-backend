from rest_framework import serializers 
from .models import Project, Feature, TechStack, ProjectImage
from portfolio.category.models import Category

class CategorySerializer(serializers.ModelSerializer): 
    image = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image', 'icon'] 

    def get_image(self, obj):
        request = self.context.get(request)
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None      

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'text']

class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ['id', 'text'] 

class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'alt_text'] 

    def get_image(self, obj):
        request = self.context.get(request)
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None    
    
class ProjectSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    tech_stacks = TechStackSerializer(many=True, read_only=True)
    category = CategorySerializer()
    image = serializers.SerializerMethodField() 
    demo_video = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = '__all__' 

    def get_image(self, obj):
        request = self.context.get(request)
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None         
    
    def get_demo_video(self, obj):
        request = self.context.get(request)
        if obj.demo_video and hasattr(obj.demo_video, 'url'):
            return request.build_absolute_uri(obj.demo_video.url) if request else obj.demo_video.url
        return None    