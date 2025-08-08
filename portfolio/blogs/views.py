from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from django.core.mail import send_mail
from django.core import signing                              # ✅ opaque token
from django.core.signing import Signer, BadSignature         # ✅ legacy + errors

from .models import Blog, Comment, Subscriber
from .serializers import (
    BlogSerializer,
    BlogListSerializer,
    BlogDetailSerializer,
    CommentSerializer,
    SubscriberSerializer,
)

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
# Create + Notify Subscribers
# -----------------------------
class BlogCreateAPIView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        blog = serializer.save()
        if not blog.is_published:
            return

        frontend = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
        read_url = f"{frontend}/blog/{blog.slug}/"

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
        # If you also send via signals, remove one to avoid duplicates.


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
    Supports BOTH formats and always redirects to a clean URL:

      - NEW (opaque token):  /api/blogs/unsubscribe/?t=<token>
      - LEGACY (signed email): /api/blogs/unsubscribe/?s=<email:signature>

    After processing, redirects to /api/blogs/unsubscribe/success/
    so no sensitive query params remain in the address bar.
    """
    email = None

    # 1) Try NEW opaque token first
    token = request.GET.get("t")
    if token:
        try:
            data = signing.loads(token, salt="newsletter-unsub", max_age=60 * 60 * 24 * 30)
            email = data.get("e")
        except BadSignature:
            return HttpResponse("Invalid or tampered link.", status=400)
        except Exception:
            return HttpResponse("Token expired or invalid.", status=400)

    # 2) Fallback to LEGACY signed email
    if email is None:
        legacy = request.GET.get("s")
        if not legacy:
            return HttpResponse(
                "Invalid or outdated link. Please use the latest email to unsubscribe.",
                status=400,
            )
        try:
            email = Signer(salt="newsletter-unsub").unsign(legacy)
        except BadSignature:
            return HttpResponse("Invalid or tampered link.", status=400)

    Subscriber.objects.filter(email=email).delete()
    return redirect("/api/blogs/unsubscribe/success/")


@api_view(["GET"])
def unsubscribe_success(request):
    return HttpResponse("You have been unsubscribed successfully.")
