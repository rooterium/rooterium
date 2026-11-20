"""Template context available on every page."""

from django.conf import settings
from django.urls import reverse

from .navigation import MAIN_NAVIGATION


def site(request):
    current = request.resolver_match
    current_name = current.view_name if current else None
    nav_items = [
        {
            "label": label,
            "url": reverse(url_name),
            "active": url_name == current_name,
        }
        for label, url_name in MAIN_NAVIGATION
    ]
    return {
        "site_name": settings.SITE_NAME,
        "site_short_name": settings.SITE_SHORT_NAME,
        "site_description": settings.SITE_DESCRIPTION,
        "nav_items": nav_items,
    }
