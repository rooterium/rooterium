from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from core.seo import SeoPageMixin


class Purpose(models.TextChoices):
    """Each purpose exists once; the footer links them in this order."""

    ABOUT = "about", _("About")
    IMPRINT = "imprint", _("Imprint")
    PRIVACY = "privacy", _("Privacy")


class SimplePage(SeoPageMixin, Page):
    """A text page: About, Imprint or Privacy (brief, section 2.9)."""

    purpose = models.CharField(
        _("purpose"),
        max_length=20,
        choices=Purpose.choices,
        unique=True,
        help_text=_(
            "Each of these pages exists once. Published pages are linked in "
            "the footer of every page."
        ),
    )
    intro = models.TextField(
        _("introduction"),
        blank=True,
        help_text=_("One or two sentences shown large under the title."),
    )
    body = RichTextField(
        _("text"),
        features=["h2", "h3", "bold", "italic", "link", "ol", "ul"],
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("purpose"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = _("text page (About, Imprint, Privacy)")
        verbose_name_plural = _("text pages")

    def get_fallback_description(self) -> str:
        return self.intro


def footer_pages() -> list[SimplePage]:
    """Live text pages in the order About, Imprint, Privacy."""
    order = {value: index for index, value in enumerate(Purpose.values)}
    return sorted(SimplePage.objects.live(), key=lambda p: order[p.purpose])


def privacy_page() -> SimplePage | None:
    return SimplePage.objects.live().filter(purpose=Purpose.PRIVACY).first()
