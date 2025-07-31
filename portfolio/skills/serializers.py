from rest_framework import serializers 
from .models import Skill, SkillCategory

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ['id', 'name']  # Only return ID and Name

class SkillSerializer(serializers.ModelSerializer):
    category = SkillCategorySerializer()  # nested category object

    class Meta:
        model = Skill
        fields = ['id', 'name', 'proficiency', 'experience_years', 'certificate_link', 'icon', 'category']
