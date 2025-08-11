from django.db import models
from django.utils.text import slugify
from portfolio.category.models import Category
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="projects"
    )

    tagline = models.CharField(max_length=160, blank=True)
    description = models.TextField()

    # Card/hero cover (optional)
    cover_image = CloudinaryField("image", blank=True, null=True)

    # 🔥 NEW: page background (optional, if you plan to use it)
    bg_image = CloudinaryField("image", blank=True, null=True)

    # Demo video (Cloudinary video)
    demo_video = CloudinaryField(
        "demo_video",
        resource_type="video",
        folder="project_videos",
        blank=True,
        null=True,
    )

    # ✅ NEW: explicit poster/thumbnail for demo_video
    demo_video_poster = CloudinaryField(
        "image",
        folder="project_posters",
        blank=True,
        null=True,
    )

    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)

    order = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "order", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["-is_featured", "order", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Project.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def primary_image(self):
        return self.project_images.first()

    def __str__(self):
        return self.title


class Feature(models.Model):
    project = models.ForeignKey(Project, related_name="features", on_delete=models.CASCADE)
    text = models.CharField(max_length=400)

    def __str__(self):
        return f"{self.project.title} • {self.text[:40]}"


class TechStack(models.Model):
    project = models.ForeignKey(Project, related_name="tech_stacks", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.title} • {self.text}"


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="project_images", on_delete=models.CASCADE)
    image = CloudinaryField("image", folder="project_images", blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.project.title}"
