import math

from django import forms
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page

from core.seo import SeoPageMixin
from core.themes import Theme, theme_label

from .blocks import StoryBodyBlock


def theme_pages():
    """Live section pages in the order of the section list."""
    order = {value: index for index, value in enumerate(Theme.values)}
    pages = (
        ThemeIndexPage.objects.live()
        .filter(theme__in=Theme.values)
        .select_related("hall_image", "descent_video")
    )
    return sorted(pages, key=lambda p: order[p.theme])


def image_field(verbose_name, help_text):
    return models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        verbose_name=verbose_name,
        help_text=help_text,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )


def video_field(verbose_name, help_text):
    """A video as a Wagtail document (MP4), served directly (ADR 0019)."""
    return models.ForeignKey(
        "wagtaildocs.Document",
        verbose_name=verbose_name,
        help_text=help_text,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )


class ThemeIndexPage(SeoPageMixin, Page):
    """A section of the temple, shown to the editor as "section page"
    (ADR 0018; internally still "theme"). Holds categories and stories."""

    theme = models.CharField(
        _("section"), max_length=20, choices=Theme.choices, unique=True
    )
    intro = models.TextField(_("introduction"), blank=True)
    root_symbol = models.CharField(
        _("root symbol"),
        max_length=60,
        blank=True,
        help_text=_('Shown under the section name in the chapel, e.g. "duduk".'),
    )
    motto = models.CharField(
        _("motto"),
        max_length=200,
        blank=True,
        help_text=_(
            'One line over the hall image, e.g. "Symbols are the language of memory."'
        ),
    )
    hall_image = image_field(
        _("hall image"),
        _("Full-width header of the section page (16:9, at least 1920 px wide)."),
    )
    descent_video = video_field(
        _("descent video"),
        _(
            "Optional MP4 played when a visitor picks this section in the "
            "chapel; it should end on the hall image. Without it the chapel "
            "fades into the hall image."
        ),
    )
    cover_image = image_field(
        _("chapel cover image"),
        _("Optional small image for the section list in the chapel."),
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("theme"),
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("root_symbol"),
                FieldPanel("motto"),
                FieldPanel("hall_image"),
                FieldPanel("descent_video"),
                FieldPanel("cover_image"),
            ],
            heading=_("Temple hall"),
        ),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["stories.CategoryPage", "stories.StoryPage"]

    class Meta:
        verbose_name = _("section page")
        verbose_name_plural = _("section pages")

    def get_fallback_description(self) -> str:
        return self.intro

    def get_theme_display(self) -> str:
        return theme_label(self.theme)

    def categories(self):
        return CategoryPage.objects.child_of(self).live().select_related("cover_image")

    def stories(self):
        """Live stories directly in the section (not in a category)."""
        return (
            StoryPage.objects.child_of(self)
            .live()
            .select_related("hero_image")
            .order_by("-date", "-pk")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["categories"] = self.categories()
        context["stories"] = self.stories()
        context["theme_pages"] = theme_pages()
        return context


class CategoryPage(SeoPageMixin, Page):
    """A group of stories inside a section, e.g. "Tree of life" in Symbols
    (ADR 0018). Its order is the page order in the section."""

    intro = models.TextField(
        _("introduction"),
        blank=True,
        help_text=_("One or two sentences: what this category covers."),
    )
    cover_image = image_field(
        _("cover image"),
        _("Optional. Without one, the card shows the title on a dark card."),
    )

    content_panels = [
        *Page.content_panels,
        FieldPanel("intro"),
        FieldPanel("cover_image"),
    ]

    parent_page_types = ["stories.ThemeIndexPage"]
    subpage_types = ["stories.StoryPage"]

    class Meta:
        verbose_name = _("category page")
        verbose_name_plural = _("category pages")

    def get_fallback_description(self) -> str:
        return self.intro

    @property
    def theme_page(self):
        return ThemeIndexPage.objects.ancestor_of(self).first()

    def stories(self):
        return (
            StoryPage.objects.child_of(self)
            .live()
            .select_related("hero_image")
            .order_by("-date", "-pk")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["stories"] = self.stories()
        context["theme_page"] = self.theme_page
        return context


class StoryPage(SeoPageMixin, Page):
    """A story ("article" to visitors). It sits in a section or in one of
    its categories; its section is the nearest section page above it
    (ADR 0018)."""

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

    parent_page_types = ["stories.ThemeIndexPage", "stories.CategoryPage"]
    subpage_types: list[str] = []

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")

    def get_fallback_description(self) -> str:
        return self.teaser

    @property
    def theme_page(self):
        """The section page this story belongs to (nearest above it)."""
        if not hasattr(self, "_theme_page"):
            self._theme_page = ThemeIndexPage.objects.ancestor_of(self).first()
        return self._theme_page

    @property
    def theme(self) -> str | None:
        return self.theme_page.theme if self.theme_page else None

    def get_theme_display(self) -> str:
        return theme_label(self.theme)

    @property
    def category(self):
        """The category page the story sits in, or None."""
        parent = self.get_parent()
        return (
            parent.specific
            if parent and parent.specific_class is CategoryPage
            else None
        )

    @property
    def reading_time(self) -> int:
        """Estimated reading time in minutes (220 words per minute)."""
        words = len(strip_tags(str(self.body.render_as_block())).split())
        words += len(self.teaser.split())
        return max(1, math.ceil(words / 220))

    def more_stories(self, limit=2):
        """Other live stories of the same section, newest first."""
        if not self.theme_page:
            return StoryPage.objects.none()
        return (
            StoryPage.objects.live()
            .descendant_of(self.theme_page)
            .exclude(pk=self.pk)
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
