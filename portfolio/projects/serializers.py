from rest_framework import serializers 
from .models import Project, Feature, TechStack, ProjectImage
from portfolio.category.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image', 'icon']

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'text']

class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ['id', 'text'] 

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'alt_text']

class ProjectSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    tech_stacks = TechStackSerializer(many=True, read_only=True)
    category = CategorySerializer()
    project_images = ProjectImageSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = '__all__'
        