from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from core import spam
from core.seo import SeoPageMixin
from newsletter.forms import SignupForm
from stories.models import image_field, video_field

from .map import map_context


class HomePage(SeoPageMixin, Page):
    """Site root. Today the interactive map (milestone 4); with the temple
    redesign the entrance: portal, entrance video, chapel (ADR 0017). The
    journey fields are optional: without them the page falls back to still
    images or plain text."""

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
        from stories.models import StoryPage

        context = super().get_context(request, *args, **kwargs)
        context.update(map_context(request))
        context["latest_stories"] = (
            StoryPage.objects.live()
            .select_related("hero_image")
            .order_by("-date", "-pk")[:3]
        )
        context["newsletter_form"] = SignupForm()
        context["started_token"] = spam.make_started_token()
        return context
