from rest_framework import serializers
from .models import Project, Feature, TechStack, ProjectImage
from portfolio.category.models import Category

# ---------- helpers (reuse everywhere) ----------
def _abs_url(request, url: str):
    """Make relative URLs absolute using request; leave absolute/Cloudinary URLs as-is."""
    if not url:
        return None
    return request.build_absolute_uri(url) if (request and isinstance(url, str) and url.startswith("/")) else url

def _safe_field_url(f):
    """Return File/CloudinaryField .url safely, avoiding public_id/raw value issues."""
    try:
        return f.url if (f and hasattr(f, "url")) else None
    except Exception:
        return None


# ---------- Category ----------
class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["name", "slug", "image", "icon"]

    def get_image(self, obj):
        request = self.context.get("request")
        img = getattr(obj, "category_image", None)
        return _abs_url(request, _safe_field_url(img))


# ---------- Simple inlines ----------
class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "text"]


class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ["id", "text"]


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ["id", "image", "alt_text"]

    def get_image(self, obj):
        request = self.context.get("request")
        return _abs_url(request, _safe_field_url(getattr(obj, "image", None)))


# ---------- Project ----------
class ProjectSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    tech_stacks = TechStackSerializer(many=True, read_only=True)
    project_images = ProjectImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    cover_image = serializers.SerializerMethodField()
    demo_video  = serializers.SerializerMethodField()
    demo_video_poster = serializers.SerializerMethodField()  # ✅ NEW
    bg_image    = serializers.SerializerMethodField()        # optional

    class Meta:
        model = Project
        fields = [
            "id", "title", "slug", "category",
            "description", "github_link", "live_link",
            "order", "is_featured", "created_at",
            "cover_image", "demo_video", "demo_video_poster", "bg_image",
            "features", "tech_stacks", "project_images",
        ]

    # ---- computed fields ----
    def get_cover_image(self, obj):
        request = self.context.get("request")

        # 1) Prefer explicit cover field if present on model
        url = _safe_field_url(getattr(obj, "cover_image", None))
        if url:
            return _abs_url(request, url)

        # 2) Fallback to common 'image' field (in case admin used it)
        url = _safe_field_url(getattr(obj, "image", None))
        if url:
            return _abs_url(request, url)

        # 3) Final fallback: first related project image
        first_rel = getattr(obj, "project_images", None)
        first = first_rel.first() if first_rel else None
        url = _safe_field_url(getattr(first, "image", None))
        return _abs_url(request, url)

    def get_demo_video(self, obj):
        request = self.context.get("request")
        url = _safe_field_url(getattr(obj, "demo_video", None))
        return _abs_url(request, url)

    def get_demo_video_poster(self, obj):
        """
        Poster priority:
        1) explicit demo_video_poster (if field exists on model)
        2) cover_image
        3) first gallery image
        """
        request = self.context.get("request")

        # 1) explicit poster
        url = _safe_field_url(getattr(obj, "demo_video_poster", None))
        if url:
            return _abs_url(request, url)

        # 2) cover image
        url = _safe_field_url(getattr(obj, "cover_image", None))
        if url:
            return _abs_url(request, url)

        # 3) first gallery image
        first_rel = getattr(obj, "project_images", None)
        first = first_rel.first() if first_rel else None
        url = _safe_field_url(getattr(first, "image", None))
        return _abs_url(request, url)

    def get_bg_image(self, obj):
        request = self.context.get("request")
        url = _safe_field_url(getattr(obj, "bg_image", None))
        return _abs_url(request, url)
