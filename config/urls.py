"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = f"{settings.SITE_SHORT_NAME} – Verwaltung"
admin.site.site_title = f"{settings.SITE_SHORT_NAME} Verwaltung"
admin.site.index_title = "Inhalte verwalten"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Feature apps go here, e.g. path("kontakt/", include("contact.urls")).
    path("", include("core.urls")),
]

if settings.DEBUG:
    # Development only: in production Caddy serves uploaded files.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
