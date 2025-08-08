from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature  # ✅ for signed unsubscribe

from .models import Blog, Comment, Subscriber
from .serializers import (
    BlogSerializer,
    BlogListSerializer,
    BlogDetailSerializer,
    CommentSerializer,
    SubscriberSerializer,
)

# Create a signer once
signer = Signer(salt="newsletter-unsub")

# -----------------------------
# Permissions
# -----------------------------
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


# -----------------------------
# Blogs (List / Detail)
# -----------------------------
class BlogListAPIView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by("-created_at")
    serializer_class = BlogListSerializer


class BlogDetailView(RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogDetailSerializer
    lookup_field = "slug"


# Optional if you still need the full serializer variant
class BlogDetailAPIView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "slug"


# -----------------------------
# CRUD for admin
# -----------------------------
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by("-created_at")
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrReadOnly]


class BlogUpdateAPIView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "id"


class BlogDeleteAPIView(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "id"


# -----------------------------
# Create + Notify Subscribers (single canonical create view)
# -----------------------------
class BlogCreateAPIView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        blog = serializer.save()

        if not blog.is_published:
            return

        # Build links
        frontend = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
        read_url = f"{frontend}/blog/{blog.slug}/"  # frontend detail page

        subject = f"🆕 New Blog Published: {blog.title}"
        message = (
            f"Hi there!\n\nA new blog has been published:\n\n"
            f"Title: {blog.title}\n\nRead it now: {read_url}\n\n"
            f"If you no longer wish to receive updates, use the unsubscribe link in the email footer."
        )

        emails = list(Subscriber.objects.values_list("email", flat=True))
        if emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=emails,
                fail_silently=False,
            )
        # NOTE: If you're also sending emails from signals.py on post_save,
        # remove one of them to avoid duplicate emails.


# -----------------------------
# Comments (list + create)
# -----------------------------
class BlogCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        blog_slug = self.kwargs["slug"]
        return Comment.objects.filter(blog__slug=blog_slug).order_by("-created_at")

    def perform_create(self, serializer):
        blog_slug = self.kwargs["slug"]
        blog = get_object_or_404(Blog, slug=blog_slug)
        comment = serializer.save(blog=blog)

        # Notify owner via email
        subject = f"📝 New Blog Comment: {blog.title}"
        message = (
            f"From: {comment.name}\n"
            f"Email: {comment.email}\n\n"
            f"Comment: {comment.content}\n"
            f"Time: {comment.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )


# -----------------------------
# CSRF (for SPA)
# -----------------------------
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set"})


# -----------------------------
# Subscribe / Unsubscribe
# -----------------------------
class SubscribeAPIView(generics.CreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


@api_view(["GET"])
def unsubscribe(request):
    """
    Secure unsubscribe via signed token:
    /api/blogs/unsubscribe/?s=<email:signature>
    """
    signed = request.GET.get("s")

    # Backward-compat: old emails had ?email=... -> reject with a hint
    if not signed:
        return HttpResponse(
            "Invalid or outdated link. Please use the latest email to unsubscribe.",
            status=400,
        )

    try:
        email = signer.unsign(signed)  # verifies signature and extracts email
    except BadSignature:
        return HttpResponse("Invalid or tampered link.", status=400)

    deleted, _ = Subscriber.objects.filter(email=email).delete()
    if deleted:
        return HttpResponse("You have been unsubscribed successfully.")
    return HttpResponse("Email not found (already unsubscribed).", status=200)
