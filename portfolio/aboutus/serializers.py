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


class AboutUsHeroSerializer(serializers.ModelSerializer):
    total_tech_experience = serializers.SerializerMethodField()

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
