from django import template

from core.seo import build_title

register = template.Library()


@register.simple_tag
def document_title(page_title=""):
    """Render the full `<title>` text for a page title."""
    return build_title(page_title)
