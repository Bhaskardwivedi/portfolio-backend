# portfolio/project/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Feature, TechStack, ProjectImage

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    classes = ["collapse"]
    show_change_link = True
    fields = ["image", "alt_text"]

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1
    classes = ["collapse"]
    fields = ["text"]

class TechStackInline(admin.TabularInline):
    model = TechStack
    extra = 1
    classes = ["collapse"]
    fields = ["text"]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # ---------- thumbnails / previews ----------
    def cover_thumb(self, obj):
        img = getattr(obj, "cover_image", None)
        if not img and hasattr(obj, "primary_image"):
            first = obj.primary_image()
            img = getattr(first, "image", None) if first else None
        url = getattr(img, "url", None)
        if url:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', url)
        return "—"
    cover_thumb.short_description = "Cover"

    def poster_thumb(self, obj):
        img = getattr(obj, "demo_video_poster", None) or getattr(obj, "cover_image", None)
        url = getattr(img, "url", None)
        if url:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', url)
        return "—"
    poster_thumb.short_description = "Poster"

    def video_preview(self, obj):
        v = getattr(obj, "demo_video", None)
        url = getattr(v, "url", None)
        if url:
            # lightweight preview (no autoplay)
            return format_html(
                '<video src="{}" style="height:50px;border-radius:6px;" preload="metadata" controls></video>',
                url,
            )
        return "—"
    video_preview.short_description = "Video"

    def media_preview(self, obj):
        """Big preview block in the form (readonly)."""
        parts = []
        # cover
        cov = getattr(obj, "cover_image", None)
        cov_url = getattr(cov, "url", None)
        if cov_url:
            parts.append(f'<div style="margin-right:10px;display:inline-block;text-align:center;">'
                         f'<div>Cover</div><img src="{cov_url}" style="height:90px;border-radius:8px;" /></div>')
        # poster
        pos = getattr(obj, "demo_video_poster", None)
        pos_url = getattr(pos, "url", None)
        if pos_url:
            parts.append(f'<div style="margin-right:10px;display:inline-block;text-align:center;">'
                         f'<div>Poster</div><img src="{pos_url}" style="height:90px;border-radius:8px;" /></div>')
        # video
        vid = getattr(obj, "demo_video", None)
        vid_url = getattr(vid, "url", None)
        if vid_url:
            parts.append(f'<div style="display:inline-block;text-align:center;">'
                         f'<div>Video</div><video src="{vid_url}" style="height:100px;border-radius:8px;" preload="metadata" controls></video></div>')
        return format_html("".join(parts)) if parts else "—"
    media_preview.short_description = "Media Preview"

    # ---------- list view ----------
    list_display = [
        "cover_thumb", "title", "category", "is_featured", "is_published",
        "order", "created_at", "poster_thumb", "video_preview"
    ]
    list_display_links = ["title"]
    list_filter  = ["category", "is_featured", "is_published", "created_at"]
    search_fields = ["title", "description", "category__name", "tech_stacks__text", "features__text"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["category"]
    list_editable = ["is_featured", "is_published", "order"]
    readonly_fields = ["created_at", "updated_at", "media_preview"]
    ordering = ["-is_featured", "order", "-created_at"]
    save_on_top = True
    list_per_page = 25

    # ---------- form layout ----------
    fieldsets = (
        ("Basics", {
            "fields": (
                ("title", "slug"),
                ("category", "order"),
                ("is_featured", "is_published"),
                "tagline",
                "description",
            )
        }),
        ("Media", {
            "fields": (
                "media_preview",              # readonly preview
                ("cover_image", "bg_image"),
                ("demo_video", "demo_video_poster"),
            )
        }),
        ("Links", {
            "fields": ("github_link", "live_link")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    inlines = [FeatureInline, TechStackInline, ProjectImageInline]

    # ---------- actions ----------
    actions = ["mark_featured", "unmark_featured", "publish", "unpublish"]

    @admin.action(description="Mark selected as Featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Unmark selected as Featured")
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description="Publish selected")
    def publish(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="Unpublish selected")
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)

    # ----------
