"""Template context available on every page."""

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse

from .navigation import MAIN_NAVIGATION


def site(request):
    current = request.resolver_match
    current_name = current.view_name if current else None
    nav_items = [
        {
            "label": label,
            "url": target if target.startswith("/") else reverse(target),
            "active": target == current_name,
        }
        for label, target in MAIN_NAVIGATION
    ]
    return {
        "site_name": settings.SITE_NAME,
        "site_short_name": settings.SITE_SHORT_NAME,
        "site_description": settings.SITE_DESCRIPTION,
        "site_owner": settings.SITE_OWNER,
        "site_native_name": settings.SITE_NATIVE_NAME,
        # Absolute URL, as Open Graph requires; pages may set `og_image`.
        "default_og_image": request.build_absolute_uri(
            static("core/img/og-default.jpg")
        ),
        "nav_items": nav_items,
        # Callables: only queried when a template uses them.
        "footer_pages": _footer_pages,
        "about_page": _about_page,
        "privacy_url": lambda: _privacy_url(request),
    }


def _footer_pages():
    from pages.models import footer_pages

    return footer_pages()


def _about_page():
    from pages.models import about_page

    return about_page()


def _privacy_url(request) -> str:
    from pages.models import privacy_page

    page = privacy_page()
    return page.get_url(request) if page else ""
