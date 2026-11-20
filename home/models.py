from django.utils.translation import gettext_lazy as _
from wagtail.models import Page

from core.seo import SeoPageMixin


class HomePage(SeoPageMixin, Page):
    """Site root. The map and teasers follow in milestone 4."""

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    # Theme index pages are added in the content model step.
    subpage_types: list[str] = []

    class Meta:
        verbose_name = _("home page")

    def get_page_title(self) -> str:
        # Empty: the home page uses the plain site title (SITE_TITLE).
        return self.seo_title
