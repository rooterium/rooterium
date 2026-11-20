import math

from django import forms
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page

from core.seo import SeoPageMixin
from core.themes import Theme

from .blocks import StoryBodyBlock


def theme_pages():
    """Live theme pages in the order of the theme list."""
    order = {value: index for index, value in enumerate(Theme.values)}
    return sorted(ThemeIndexPage.objects.live(), key=lambda p: order[p.theme])


class ThemeIndexPage(SeoPageMixin, Page):
    """One page per theme; lists its stories (ADR 0014)."""

    theme = models.CharField(
        _("theme"), max_length=20, choices=Theme.choices, unique=True
    )
    intro = models.TextField(_("introduction"), blank=True)

    content_panels = [*Page.content_panels, FieldPanel("theme"), FieldPanel("intro")]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["stories.StoryPage"]

    class Meta:
        verbose_name = _("theme page")
        verbose_name_plural = _("theme pages")

    def get_fallback_description(self) -> str:
        return self.intro

    def stories(self):
        return StoryPage.objects.child_of(self).live().order_by("-date", "-pk")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["stories"] = self.stories()
        context["theme_pages"] = theme_pages()
        return context


class StoryPage(SeoPageMixin, Page):
    """A story. Its theme is the theme of its parent page (ADR 0014)."""

    date = models.DateField(
        _("date"), default=timezone.localdate, help_text=_("Shown on the story.")
    )
    teaser = models.TextField(
        _("teaser"),
        max_length=300,
        help_text=_("One or two sentences for story cards and search engines."),
    )
    hero_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        verbose_name=_("hero image"),
        on_delete=models.PROTECT,
        related_name="+",
    )
    body = StreamField(StoryBodyBlock(), verbose_name=_("body"))
    related_places = ParentalManyToManyField(
        "places.Place",
        verbose_name=_("related places"),
        blank=True,
        related_name="stories",
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("date"),
        FieldPanel("teaser"),
        FieldPanel("hero_image"),
        FieldPanel("body"),
        InlinePanel("sources", heading=_("Sources"), label=_("Source")),
        FieldPanel("related_places", widget=forms.CheckboxSelectMultiple),
    ]

    parent_page_types = ["stories.ThemeIndexPage"]
    subpage_types: list[str] = []

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")

    def get_fallback_description(self) -> str:
        return self.teaser

    @property
    def theme(self) -> str | None:
        parent = self.get_parent()
        return getattr(parent.specific, "theme", None) if parent else None

    def get_theme_display(self) -> str:
        return Theme(self.theme).label if self.theme else ""

    @property
    def theme_page(self):
        parent = self.get_parent()
        return parent.specific if parent else None

    @property
    def reading_time(self) -> int:
        """Estimated reading time in minutes (220 words per minute)."""
        words = len(strip_tags(str(self.body.render_as_block())).split())
        words += len(self.teaser.split())
        return max(1, math.ceil(words / 220))

    def more_stories(self, limit=2):
        """Other live stories of the same theme, newest first."""
        return (
            StoryPage.objects.live()
            .sibling_of(self, inclusive=False)
            .select_related("hero_image")
            .order_by("-date", "-pk")[:limit]
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related_places"] = self.related_places.filter(live=True)
        context["more_stories"] = self.more_stories()
        if self.hero_image_id:
            context["og_image"] = request.build_absolute_uri(
                self.hero_image.get_rendition("fill-1200x630").url
            )
        return context


class StorySource(Orderable):
    page = ParentalKey(StoryPage, related_name="sources", on_delete=models.CASCADE)
    title = models.CharField(
        _("title"), max_length=300, help_text=_("Book, article or video title.")
    )
    url = models.URLField(_("link"), blank=True)
    note = models.CharField(
        _("note"),
        max_length=300,
        blank=True,
        help_text=_("e.g. author, publisher, year, page."),
    )

    panels = [FieldPanel("title"), FieldPanel("url"), FieldPanel("note")]

    class Meta(Orderable.Meta):
        verbose_name = _("source")
        verbose_name_plural = _("sources")

    def __str__(self):
        return self.title
