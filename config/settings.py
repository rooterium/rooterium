"""Django settings.

All environment-specific values come from environment variables (see
`.env.example`). There is a single settings module; development and
production differ only in their environment.
"""

import sys
import tempfile
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# Read a local .env file if present. In Docker the variables are injected by
# Compose instead, so a missing file is fine.
environ.Env.read_env(BASE_DIR / ".env")

# --- Core -----------------------------------------------------------------

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    # First, so its templates can override Django's (e.g. admin templates).
    "core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail CMS (ADR 0009). No wagtail.embeds: YouTube is embedded without
    # oEmbed requests (ADR 0013, 0014).
    "wagtail.contrib.redirects",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # Project apps
    "images",
    "home",
    "stories",
    "places",
    "events",
    "projects",
    "newsletter",
    "submissions",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves static files in production (Gunicorn does not).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "core.middleware.ContentSecurityPolicyMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database -------------------------------------------------------------

# PostgreSQL only (ADR 0003), e.g. postgres://user:password@db:5432/app
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentication -------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation -------------------------------------------------

# Website language: English first; Armenian and Russian later (ADR 0012).
# All user-facing strings are translatable from day one.
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Vienna"
USE_I18N = True
USE_TZ = True

# --- Static and media files -----------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = env.path("STATIC_ROOT", default=BASE_DIR / "staticfiles")

MEDIA_URL = "media/"
MEDIA_ROOT = env.path("MEDIA_ROOT", default=BASE_DIR / "media")

# Static files get hashed names and are pre-compressed at build time, so they
# can be cached forever. The manifest only exists after collectstatic (image
# build); tests run without it and use the plain storage.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
if "test" in sys.argv[1:2]:
    STORAGES["staticfiles"]["BACKEND"] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    # Uploaded test images go to a throwaway folder, not the real media.
    MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="rooterium-test-media-"))

# --- Site -----------------------------------------------------------------

# Replace the placeholders when creating a project (docs/NEW_PROJECT.md).
SITE_NAME = "Rooterium"
SITE_SHORT_NAME = "Rooterium"
# Document title of the home page; other pages use "<page> – <short name>".
SITE_TITLE = f"{SITE_NAME} – Find your way back to your roots"
# Armenian name next to the logo (variant B mockup). Empty until the editor
# confirms the exact wording: Armenian script only from verified sources
# (brief, section 6).
SITE_NATIVE_NAME = ""
# Shown in the footer ("a personal project by …"). Replace the placeholder
# with the editor's name once they agree to be named.
SITE_OWNER = "[Name]"
# Default meta description for pages that do not set their own.
SITE_DESCRIPTION = (
    "Armenian history, traditions, myths, symbols and music, collected and "
    "connected – for Armenians all over the world and everyone curious about "
    "their roots."
)
# Git commit of the running image (Dockerfile build arg GIT_COMMIT, set by CI),
# shown at /version. "dev" for local builds.
APP_COMMIT = env("APP_COMMIT", default="dev")

# --- Wagtail --------------------------------------------------------------

WAGTAIL_SITE_NAME = SITE_NAME
# Base URL for links in admin notification emails: the first trusted origin
# in production (e.g. https://example.org), localhost in development.
WAGTAILADMIN_BASE_URL = (
    CSRF_TRUSTED_ORIGINS[0] if CSRF_TRUSTED_ORIGINS else "http://localhost:8000"
)
# Images with required alt text, credit and licence (ADR 0014).
WAGTAILIMAGES_IMAGE_MODEL = "images.CustomImage"
# Documents: PDFs and the temple videos (MP4, ADR 0019). Served directly
# from MEDIA_ROOT (Caddy in production, core.dev_media locally) so videos
# get range requests; every document is public by its URL.
WAGTAILDOCS_EXTENSIONS = ["pdf", "mp4"]
WAGTAILDOCS_SERVE_METHOD = "direct"
# Search in PostgreSQL, no external search service.
WAGTAILSEARCH_BACKENDS = {"default": {"BACKEND": "wagtail.search.backends.database"}}
# Localisation is prepared but not enabled in version 1 (ADR 0012).
WAGTAIL_I18N_ENABLED = False

# --- Email ----------------------------------------------------------------

# Development prints emails to the console; production uses SMTP (.env).
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=465)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=True)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Receives the "Suggest an event / a project" notifications. Empty: no
# email (the drafts still show up in the admin).
EDITOR_NOTIFICATION_EMAIL = env("EDITOR_NOTIFICATION_EMAIL", default="")

# --- Logging --------------------------------------------------------------

# Log to stdout/stderr; Docker collects the output.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        # 404/403 are expected noise; access logs come from Caddy.
        "django.request": {"level": "ERROR"},
        # Wagtail runs its background tasks in the request and logs every
        # task and page action at INFO; Wagtail's own audit log (in the
        # database) already records the page actions.
        "django_tasks": {"level": "WARNING"},
        "wagtail": {"level": "WARNING"},
    },
}

# --- Security (production) ------------------------------------------------

# Caddy terminates TLS and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content-Security-Policy for public pages (ADR 0013, core/middleware.py):
# everything from our own origin; YouTube only as a nocookie frame after a
# click (milestone 5). A new source needs an ADR.
CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "frame-src": ["https://www.youtube-nocookie.com"],
    "object-src": ["'none'"],
    "base-uri": ["'self'"],
    "form-action": ["'self'"],
    "frame-ancestors": ["'none'"],
}

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
