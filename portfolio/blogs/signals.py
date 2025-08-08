
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.signing import Signer  
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Blog, Subscriber

print("🧭 signals.py imported")

signer = Signer(salt="newsletter-unsub")  

@receiver(post_save, sender=Blog)
def send_blog_to_subscribers(sender, instance, created, **kwargs):
    if not created:
        return

    base_fe = getattr(settings, "FRONTEND_BASE_URL", "https://bhaskarai.com").rstrip("/")
    base_be = getattr(settings, "BACKEND_BASE_URL", "https://api.bhaskarai.com").rstrip("/")

    title = instance.title
    content = (instance.content[:150] + "...") if len(instance.content) > 150 else instance.content
    read_url = f"{base_fe}/blog/{instance.slug}/"

    for email in Subscriber.objects.values_list("email", flat=True):
        signed = signer.sign(email)  
        unsubscribe_url = f"{base_be}/api/blogs/unsubscribe/?s={signed}" 

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;border:1px solid #ddd;">
            <h2 style="color:#e67e22;">📰 New Blog Alert!</h2>
            <h3 style="color:#2c3e50;">{title}</h3>
            <p style="color:#555;">{content}</p>
            <a href="{read_url}" style="display:inline-block;margin-top:15px;padding:10px 20px;background:#e67e22;color:#fff;text-decoration:none;border-radius:5px;">Read Full Blog</a>
            <p style="margin-top:20px;color:#999;font-size:12px;">You're receiving this because you subscribed to Bhaskar.AI newsletter.</p>
            <p style="margin-top:10px;font-size:12px;color:#888;">
                If you no longer wish to receive updates, you can
                <a href="{unsubscribe_url}" style="color:#e74c3c;">unsubscribe here</a>.
            </p>
        </div>
        """

        msg = EmailMessage(
            subject=f"New Blog Published: {title}",
            body=html,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
