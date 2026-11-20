"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

admin_title = _("%(site)s administration") % {"site": settings.SITE_SHORT_NAME}
admin.site.site_header = admin_title
admin.site.site_title = admin_title
admin.site.index_title = _("Manage content")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Feature apps go here, e.g. path("events/", include("events.urls")).
    path("", include("core.urls")),
]

if settings.DEBUG:
    # Development only: in production Caddy serves uploaded files.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
