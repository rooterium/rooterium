from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from core.seo import SeoPageMixin
from stories.models import image_field, theme_pages, video_field


class HomePage(SeoPageMixin, Page):
    """Site root: the temple entrance (ADR 0017). Portal, entrance video and
    chapel with the six sections; the map lives at /map/. The journey fields
    are optional: without them the page falls back to still images or plain
    text, and core/js/journey.js only adds the videos."""

    tagline = models.CharField(
        _("tagline"),
        max_length=200,
        blank=True,
        help_text=_("One line under the title on the portal screen."),
    )
    chapel_heading = models.CharField(
        _("chapel heading"),
        max_length=100,
        blank=True,
        help_text=_('Heading over the list of sections, e.g. "Choose a path".'),
    )
    portal_poster = image_field(
        _("portal image"),
        _(
            "Still of the portal: shown while the portal video loads and "
            "instead of it (reduced motion, data saver, no JavaScript)."
        ),
    )
    portal_video = video_field(
        _("portal video"),
        _("Short MP4 loop of the portal, without sound; first and last frame alike."),
    )
    entrance_video = video_field(
        _("entrance video"),
        _('MP4 played once after "Enter"; it should end on the chapel image.'),
    )
    chapel_image = image_field(
        _("chapel image"),
        _("Still of the chapel, behind the list of sections."),
    )

    content_panels = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("tagline"),
                FieldPanel("portal_poster"),
                FieldPanel("portal_video"),
                FieldPanel("entrance_video"),
                FieldPanel("chapel_heading"),
                FieldPanel("chapel_image"),
            ],
            heading=_("Temple entrance"),
        ),
    ]

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["stories.ThemeIndexPage", "pages.SimplePage"]

    class Meta:
        verbose_name = _("home page")

    def get_page_title(self) -> str:
        # Empty: the home page uses the plain site title (SITE_TITLE).
        return self.seo_title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Every live section, also those without stories yet (brief, 6).
        context["sections"] = theme_pages()
        return context
