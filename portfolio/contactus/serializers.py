from rest_framework import serializers
from .models import contactMessage, contactinfo

class ContactMessageSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = contactMessage 
        fields = '__all__'
        

class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = contactinfo
        fields = '__all__'

