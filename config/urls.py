"""Root URL configuration."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from core import dev_media

admin_title = _("%(site)s administration") % {"site": settings.SITE_SHORT_NAME}
admin.site.site_header = admin_title
admin.site.site_title = admin_title
admin.site.index_title = _("Manage content")

urlpatterns = [
    # Django admin for technical tasks only; editors use the Wagtail admin
    # (ADR 0014).
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Feature apps go here, e.g. path("events/", include("events.urls")).
    path("", include("core.urls")),
    # Wagtail pages last: it catches every remaining path.
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    # Development only: in production Caddy serves uploaded files. With
    # range requests, which the map tiles need (ADR 0015). Before the
    # Wagtail catch-all.
    urlpatterns.insert(
        0, re_path(r"^media/(?P<path>.+)$", dev_media.serve_media, name="media")
    )
