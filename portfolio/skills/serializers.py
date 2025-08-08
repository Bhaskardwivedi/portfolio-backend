from rest_framework import serializers 
from .models import Skill, SkillCategory

class SkillCategorySerializer(serializers.ModelSerializer): 
    category_icon = serializers.SerializerMethodField()
    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'category_icon'] 

    def get_category_icon(self, obj):
        request = self.context.get('request')
        if obj.category_icon and hasattr(obj.category_icon, 'url'):
            return request.build_absolute_uri(obj.category_icon.url) if request else obj.category_icon.url
        return None


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