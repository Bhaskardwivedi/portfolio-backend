from rest_framework import serializers
from .models import Service, ServiceFeature, Category  # ✅ sab models yahan import kar

# ✅ Feature serializer
class ServiceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFeature
        fields = ['id', 'point']

# ✅ Category serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'type']

# ✅ Service serializer with nested category + features
class ServiceSerializer(serializers.ModelSerializer):
    features = ServiceFeatureSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
