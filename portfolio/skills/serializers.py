from rest_framework import serializers 
from .models import Skill, SkillCategory

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ['id', 'name']  # Only return ID and Name

class SkillSerializer(serializers.ModelSerializer):
    category = SkillCategorySerializer()
    icon = serializers.SerializerMethodField()


    class Meta:
        model = Skill
        fields = ['id', 'name', 'proficiency', 'experience_years', 'certificate_link', 'icon', 'category']

    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None