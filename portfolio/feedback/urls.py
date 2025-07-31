from django.urls import path
from .views import FeedbackCreateView, FeedbackListView

urlpatterns = [
    path('feedback/', FeedbackCreateView.as_view(), name='create-feedback'),
    path('testimonials/', FeedbackListView.as_view(), name='list-feedback'),
]
