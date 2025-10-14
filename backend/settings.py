"""
Django settings for backend project.
"""

from pathlib import Path
import os
import base64
from dotenv import load_dotenv
import dj_database_url
import cloudinary

# -----------------------------------------------------------------------------
# Base / env
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()  # local .env for dev only

def env_bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

def env_list(key: str, default=None, sep=","):
    v = os.getenv(key)
    if not v:
        return default or []
    return [x.strip() for x in v.split(sep) if x.strip()]

# -----------------------------------------------------------------------------
# Security / debug
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "CHANGE-ME-IN-PROD")
DEBUG = env_bool("DEBUG", True)

# Use env list if provided, otherwise your defaults
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    ["api.bhaskarai.com", "bhaskarai.com", "localhost", "127.0.0.1"],
)

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://bhaskarai.com")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "https://api.bhaskarai.com")

# -----------------------------------------------------------------------------
# Restore Google API files from Railway env (Base64 or raw JSON)
# -----------------------------------------------------------------------------
def _write_file_from_env(var: str, path: str):
    data = os.getenv(var)
    if not data:
        return
    try:
        # if it’s base64 we decode; if not, we just write raw JSON
        data = base64.b64decode(data).decode()
    except Exception:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

# Will create files next to manage.py at runtime (Railway)
_write_file_from_env("GOOGLE_CREDENTIALS_JSON", str(BASE_DIR / "credentials.json"))
_write_file_from_env("GOOGLE_TOKEN_JSON", str(BASE_DIR / "token.json"))

# -----------------------------------------------------------------------------
# Third-party service envs (Zoom / OpenAI etc.)
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_BASE_URL = os.getenv("ZOOM_BASE_URL", "https://api.zoom.us")
ZOOM_HOST_EMAIL = os.getenv("ZOOM_HOST_EMAIL")  # assistant@bhaskarai.com

# -----------------------------------------------------------------------------
# Installed apps / middleware
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # your apps
    "portfolio.projects",
    "portfolio.blogs.apps.BlogsConfig",
    "portfolio.skills",
    "portfolio.contactus",
    "portfolio.chatwithus",
    "portfolio.services",
    "portfolio.aboutus.apps.AboutusConfig",
    "portfolio.socials",
    "portfolio.feedback",
    "portfolio.category.apps.CategoryConfig",

    # third party
    "cloudinary",
    "cloudinary_storage",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}

# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"     # store in UTC; convert on edges
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static / media
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -----------------------------------------------------------------------------
# Cloudinary
# -----------------------------------------------------------------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", False)
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    [
        "https://bhaskarai.com",
        "https://api.bhaskarai.com",
        "http://localhost:5173",
        "http://192.168.31.164:5173",
    ],
)
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    [
        "https://api.bhaskarai.com",
        "https://bhaskarai.com",
        "http://localhost:5173",
        "http://192.168.31.164:5173",
    ],
)

# -----------------------------------------------------------------------------
# DRF
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}

# -----------------------------------------------------------------------------
# Email (Gmail SMTP fallback if you still need it)
# Prefer Gmail API via gmail_utils; keep SMTP only if required.
# -----------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "bhaskardwivedi544@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "change-me")  # use app password in env
