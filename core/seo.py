"""Page titles and meta descriptions.

Every public view uses `SeoMixin` (or passes `page_title` and
`meta_description` into the template context itself). The base template
renders `<title>`, `<meta name="description">` and the Open Graph tags from
these values, falling back to the site defaults from settings.
"""

from django.conf import settings


def build_title(page_title: str = "") -> str:
    """Return the full document title, e.g. "Kontakt – Kurzname"."""
    if not page_title:
        return settings.SITE_TITLE
    return f"{page_title} – {settings.SITE_SHORT_NAME}"


class SeoMixin:
    """Adds `page_title` and `meta_description` to the template context.

    Set the class attributes for static pages, or override the getters for
    pages whose title depends on an object.
    """

    page_title = ""
    meta_description = ""

    def get_page_title(self) -> str:
        return self.page_title

    def get_meta_description(self) -> str:
        return self.meta_description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        context["meta_description"] = self.get_meta_description()
        return context
