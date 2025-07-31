from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Blog, Subscriber

@receiver(post_save, sender=Blog)
def send_blog_to_subscribers(sender, instance, created, **kwargs):
    if created:
        title = instance.title
        slug = instance.slug
        content = instance.content[:150] + "..." if len(instance.content) > 150 else instance.content
        blog_url = f"http://192.168.31.164:5173/blog/{slug}"

        subject = f"📰 New Blog Published: {title}"

        subscribers = Subscriber.objects.values_list('email', flat=True)
        
        for subscriber_email in subscribers:
            # ✅ Corrected the unsubscribe URL path
            unsubscribe_link = f"http://192.168.31.164:8000/api/blogs/unsubscribe/?email={subscriber_email}"

            html_message = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;border:1px solid #ddd;">
                <h2 style="color:#e67e22;">📰 New Blog Alert!</h2>
                <h3 style="color:#2c3e50;">{title}</h3>
                <p style="color:#555;">{content}</p>
                <a href="{blog_url}" style="display:inline-block;margin-top:15px;padding:10px 20px;background:#e67e22;color:#fff;text-decoration:none;border-radius:5px;">Read Full Blog</a>
                <p style="margin-top:20px;color:#999;font-size:12px;">You're receiving this because you subscribed to Bhaskar.AI newsletter.</p>
                <p style="margin-top:30px;font-size:12px;color:#888;">
                    If you no longer wish to receive updates, you can 
                    <a href="{unsubscribe_link}" style="color:#e74c3c;">unsubscribe here</a>.
                </p>
            </div>
            """

            msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[subscriber_email],
            )
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
