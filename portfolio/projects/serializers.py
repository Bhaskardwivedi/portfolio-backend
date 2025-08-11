from rest_framework import serializers
from .models import Project, Feature, TechStack, ProjectImage
from portfolio.category.models import Category

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["name", "slug", "image", "icon"]

    def get_image(self, obj):
        request = self.context.get('request')
        img = getattr(obj, "category_image", None)   
        if img and hasattr(img, "url"):
            url = img.url
            return request.build_absolute_uri(url) if request else url
        return None


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "text"]


class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ["id", "text"]


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ["id", "image", "alt_text"]

    def get_image(self, obj):
        request = self.context.get('request')
        if getattr(obj, "image", None) and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProjectSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    tech_stacks = TechStackSerializer(many=True, read_only=True)
    project_images = ProjectImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    cover_image = serializers.SerializerMethodField()
    demo_video = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "slug", "category",
            "description", "github_link", "live_link",
            "order", "is_featured", "created_at",
            "cover_image", "demo_video",
            "features", "tech_stacks", "project_images",
        ]

    def get_cover_image(self, obj):
        # first project image as cover
        first = obj.project_images.first()
        if not first:
            return None
        request = self.context.get('request')
        url = first.image.url if hasattr(first.image, "url") else None
        return request.build_absolute_uri(url) if (request and url) else url

    def get_demo_video(self, obj):
        if not obj.demo_video:
            return None
        request = self.context.get('request')
        url = obj.demo_video.url if hasattr(obj.demo_video, "url") else None
        return request.build_absolute_uri(url) if (request and url) else url
