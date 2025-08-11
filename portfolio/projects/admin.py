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
    # thumbnail helper (null-safe)
    def cover_thumb(self, obj):
        img = None
        # try cover_image if present
        if hasattr(obj, "cover_image") and getattr(obj, "cover_image", None):
            img = obj.cover_image
        # fallback to first project image
        if not img and hasattr(obj, "primary_image"):
            first = obj.primary_image()
            if first and getattr(first, "image", None):
                img = first.image
        if img and hasattr(img, "url"):
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />', img.url
            )
        return "—"
    cover_thumb.short_description = "Cover"

    list_display = ["cover_thumb", "title", "category", "is_featured", "order", "created_at"]
    list_filter  = ["category", "is_featured", "created_at"]
    search_fields = ["title", "description", "category__name", "tech_stacks__text", "features__text"]
    prepopulated_fields = {"slug": ("title",)}

    # ❌ remove autocomplete to avoid CategoryAdmin dependency
    # autocomplete_fields = ["category"]
    # ✅ fast lookup without changing Category admin
    raw_id_fields = ["category"]

    list_editable = ["is_featured", "order"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-is_featured", "order", "-created_at"]
    save_on_top = True
    list_per_page = 25

    inlines = [FeatureInline, TechStackInline, ProjectImageInline]

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ["project", "alt_text"]
    search_fields = ["project__title", "alt_text"]

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["project", "text"]
    search_fields = ["project__title", "text"]

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ["project", "text"]
    search_fields = ["project__title", "text"]
