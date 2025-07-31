from rest_framework import serializers
from .models import Blog, Comment, Subscriber

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__' 

class BlogListSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField() 
    

    class Meta: 
        model = Blog 
        fields = ['id', 'title', 'summary', 'image', 'created_at', 'slug'] 

    def get_summary(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content', 'created_at']

class BlogDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = '__all__'
        
class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email']
