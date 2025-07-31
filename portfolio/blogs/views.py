from rest_framework import generics, viewsets, permissions
from .models import Blog, Comment, Subscriber
from .serializers import BlogSerializer, BlogListSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import CommentSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from .serializers import BlogDetailSerializer, SubscriberSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse



class BlogListAPIView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogListSerializer

class BlogDetailView(RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogDetailSerializer
    lookup_field = 'slug'

class BlogDetailAPIView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'



class BlogCreateAPIView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    def perform_create(self, serializer):
        blog = serializer.save()

        subscribers = Subscriber.objects.all()

        subject = f"New Blog Published: {blog.title}"
        message = f"Hi,\n\nA new blog has been published on the website.\n\nTitle: {blog.title}\n\nRead here: https://yourdomain.com/blog/{blog.slug}"

        for subscriber in subscribers:
            send_mail(
                subject,
                message,
                'bhaskardwivedi544@gmail.com',  
                [subscriber.email],
                fail_silently=True,
            )

class BlogUpdateAPIView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'id'



class BlogDeleteAPIView(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'id'



class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrReadOnly]

class BlogCommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'blog_id'

    def get_queryset(self):
        blog_slug = self.kwargs['slug']
        return Comment.objects.filter(blog__slug=blog_slug).order_by('-created_at')
    
    def perform_create(self, serializer):
        blog_slug = self.kwargs['slug']
        blog = Blog.objects.get(slug=blog_slug)
        comment = serializer.save(blog=blog)

        title = blog.title if isinstance(blog.title, str) else str(blog.title)
        subject = f"📝 New Blog Comment: {title}"
        message = (
            f"From: {comment.name}\n\n"
            f"Email: {comment.email}\n\n"
            f"Comment:{comment.content}\n\n"
             f"Time: {comment.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ) 
        send_mail(
            subject=subject,
            message=message,
            from_email=Comment.email,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
    
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'message': 'CSRF cookie set'})
    

class SubscribeAPIView(generics.CreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    
class BlogCreateAPIView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        blog = serializer.save()
        
        from .models import Subscriber
        subscribers = Subscriber.objects.all()
        emails = [sub.email for sub in subscribers]

        if blog.is_published:
            subject = f"🆕 New Blog Published: {blog.title}"
            message = f"Hi there!\n\nA new blog has been published:\n\nTitle: {blog.title}\n\nRead it now at: http://localhost:8000/blogs/{blog.slug}/"
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                emails,
                fail_silently=False,
            )

@api_view(['GET'])
def unsubscribe(request):
    email = request.GET.get('email')
    if email:
        Subscriber.objects.filter(email=email).delete()
        return HttpResponse("You have been unsubscribed successfully.")
    return HttpResponse("Invalid unsubscribe request.", status=400)
