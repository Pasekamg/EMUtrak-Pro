from pathlib import Path
import os
from datetime import timedelta
from corsheaders.defaults import default_headers

# ---------------- Core ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DEBUG", "1") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-change-me")

def _split_env(name: str, default: str = "") -> list[str]:
    return [s.strip() for s in os.getenv(name, default).split(",") if s.strip()]

ALLOWED_HOSTS = _split_env("ALLOWED_HOSTS", "127.0.0.1,localhost")

# ---------------- Apps ----------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    # Local
    "core",
]

# ---------------- Middleware (CORS high, after Session) ----------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # high in the stack
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "emutrak_api.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "emutrak_api.wsgi.application"

# ---------------- Database ----------------
# Use SQLite for dev; switch to Postgres by setting DATABASE_URL.
# If dj-database-url isn't installed, we silently fall back to SQLite.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
_db_url = os.getenv("DATABASE_URL")
if _db_url:
    try:
        import dj_database_url
        DATABASES = {"default": dj_database_url.parse(_db_url, conn_max_age=600)}
    except ImportError:
        # Optional: log a warning in real projects
        pass

# ---------------- Auth / DRF / JWT ----------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ---------------- Swagger / OpenAPI ----------------
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Example: Bearer <token>",
        }
    },
}
# Tip: In urls.py, set `permission_classes=[AllowAny]` on your schema views.

# ---------------- Internationalization / TZ ----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Johannesburg"
USE_I18N = True
USE_TZ = True

# ---------------- Static / Media ----------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- CORS / CSRF ----------------
# Keep ALL_ORIGINS False; list trusted frontends via env. Defaults include GitHub Pages + local dev ports.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = _split_env(
    "CORS_ALLOWED_ORIGINS",
    "https://pasekamg.github.io,"
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:8000,"
    "http://127.0.0.1:5500,http://localhost:5500"
)

# Allow a custom header from your frontend (in addition to standard defaults, which already include Authorization)
CORS_ALLOW_HEADERS = list(default_headers) + ["x-role"]

# Trust secure (https) CORS origins for CSRF, plus common local dev hosts
CSRF_TRUSTED_ORIGINS = [o for o in CORS_ALLOWED_ORIGINS if o.startswith("https://")]
CSRF_TRUSTED_ORIGINS += ["http://127.0.0.1:5500", "http://localhost:5500"]

# ---------------- Security (enable when behind HTTPS in prod) ----------------
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "0") == "1"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if (not DEBUG and SECURE_SSL_REDIRECT) else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
