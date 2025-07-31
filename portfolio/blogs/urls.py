from django.urls import path
from .views import (
    BlogListAPIView,
    BlogDetailAPIView,
    BlogCreateAPIView,
    BlogUpdateAPIView,
    BlogDeleteAPIView,
    BlogCommentListCreateAPIView,
    BlogDetailView, SubscribeAPIView, unsubscribe
)

urlpatterns = [
    path('subscribe/', SubscribeAPIView.as_view(), name='blog-subscribe'),                        
    path('create/', BlogCreateAPIView.as_view(), name='blog-create'),      
    path('unsubscribe/', unsubscribe, name='blog-unsubscribe'),        
    path('update/<int:id>/', BlogUpdateAPIView.as_view(), name='update-blog'),    
    path('delete/<int:id>/', BlogDeleteAPIView.as_view(), name='delete-blog'),  
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),  
    path('<slug:slug>/comments/', BlogCommentListCreateAPIView.as_view(), name='comment-detail'),
    path('', BlogListAPIView.as_view(), name='blog-list'),
]
