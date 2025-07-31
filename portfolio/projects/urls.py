from django.urls import path
from .views import ProjectListAPIView

urlpatterns = [
    path('', ProjectListAPIView.as_view(), name='project-list'),
]