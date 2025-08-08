from django.conf import settings
from django.core.mail import EmailMessage

def send_new_blog_email(blog, emails):
    fe = settings.FRONTEND_BASE_URL.rstrip("/")
    be = settings.BACKEND_BASE_URL.rstrip("/")
    read_url = f"{fe}/blog/{blog.slug}/"
    unsubscribe_url = f"{be}/api/blogs/unsubscribe/?email={{EMAIL}}"  

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;border:1px solid #ddd;">
      <h2 style="color:#e67e22;">📰 New Blog Alert!</h2>
      <h3 style="color:#2c3e50;">{blog.title}</h3>
      <p style="color:#555;">{(blog.content[:150]+'...') if len(blog.content)>150 else blog.content}</p>
      <a href="{read_url}" style="display:inline-block;margin-top:15px;padding:10px 20px;background:#e67e22;color:#fff;text-decoration:none;border-radius:5px;">Read Full Blog</a>
      <p style="margin-top:20px;color:#999;font-size:12px;">You're receiving this because you subscribed to Bhaskar.AI newsletter.</p>
      <p style="margin-top:10px;font-size:12px;color:#888;">If you no longer wish to receive updates, you can
        <a href="{unsubscribe_url}" style="color:#e74c3c;">unsubscribe here</a>.
      </p>
    </div>
    """

    for email in emails:
        msg = EmailMessage(
            subject=f"New Blog Published: {blog.title}",
            body=html.replace("{EMAIL}", email),
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
