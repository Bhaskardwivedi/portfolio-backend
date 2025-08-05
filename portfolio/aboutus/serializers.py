from rest_framework import serializers
from .models import AboutUs, Experience
from datetime import datetime


class ExperienceSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    total_years = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            'job_title',
            'company_name',
            'start_year',
            'end_year',
            'is_tech',
            'is_current',
            'description',
            'duration',
            'total_years',
        ]

    def get_duration(self, obj):
        end_year = obj.end_year if obj.end_year else datetime.now().year
        return f"{obj.start_year} - {'Present' if obj.is_current else obj.end_year}"

    def get_total_years(self, obj):
        end_year = obj.end_year if obj.end_year else datetime.now().year
        return end_year - obj.start_year


class AboutUsSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)
    total_tech_experience = serializers.SerializerMethodField()
    aboutus_image = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()

    class Meta:
        model = AboutUs
        fields = [
            'name',
            'title',
            'headline',
            'description',
            'total_projects',
            'total_clients',
            'aboutus_image',
            'resume',
            'total_tech_experience',
            'experiences',
        ]
        read_only_fields = ('updated_at',)

    def get_total_tech_experience(self, obj):
        return obj.total_tech_experience
    
    def get_aboutus_image(self, obj):
        request = self.context.get('request')
        if obj.aboutus_image and hasattr(obj.aboutus_image, 'url'):
            return request.build_absolute_uri(obj.aboutus_image.url) if request else obj.aboutus_image.url
        return None

    def get_resume(self, obj):
        if obj.resume and hasattr(obj.resume, 'public_id') and hasattr(obj.resume, 'format'):
            cloud_name = "dkiii8j7g"  
            public_id = obj.resume.public_id
            extension = obj.resume.format
            filename = "resume"
            download_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/fl_attachment:{filename}/{public_id}.{extension}"
            return download_url
        return None

class AboutUsHeroSerializer(serializers.ModelSerializer):
    total_tech_experience = serializers.SerializerMethodField()
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = AboutUs
        fields = [
            'name',
            'title',
            'headline',
            'hero_image',
            'total_tech_experience',
            'total_projects',
            'total_clients'
        ]

    def get_total_tech_experience(self, obj):
        return obj.total_tech_experience
    
    def get_hero_image(self, obj):
        request = self.context.get('request')
        if obj.hero_image and hasattr(obj.hero_image, 'url'):
            return request.build_absolute_uri(obj.hero_image.url) if request else obj.hero_image.url
        return None
    
    