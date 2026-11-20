"""StreamField blocks for story bodies (ADR 0014)."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock

YOUTUBE_ID = re.compile(
    r"^https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/)"
    r"|youtu\.be/|youtube-nocookie\.com/embed/)([A-Za-z0-9_-]{11})"
)


def youtube_id(url: str) -> str | None:
    match = YOUTUBE_ID.match(url or "")
    return match.group(1) if match else None


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(label=_("Text"))
    level = blocks.ChoiceBlock(
        choices=[("h2", _("Heading")), ("h3", _("Subheading"))],
        default="h2",
        label=_("Level"),
    )

    class Meta:
        icon = "title"
        label = _("Heading")
        template = "stories/blocks/heading.html"


class QuoteBlock(blocks.StructBlock):
    text = blocks.TextBlock(label=_("Quote"))
    source = blocks.CharBlock(label=_("Source"), help_text=_("Who said or wrote it."))
    source_url = blocks.URLBlock(required=False, label=_("Source link"))

    class Meta:
        icon = "openquote"
        label = _("Quote")
        template = "stories/blocks/quote.html"


class StoryImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(
        label=_("Image"), help_text=_("Alt text and credit come from the image.")
    )
    caption = blocks.CharBlock(required=False, label=_("Caption"))

    class Meta:
        icon = "image"
        label = _("Image")
        template = "stories/blocks/image.html"


class YouTubeValue(blocks.StructValue):
    def video_id(self):
        return youtube_id(self.get("url"))


class YouTubeBlock(blocks.StructBlock):
    """A YouTube video, embedded via youtube-nocookie.com only after a click
    (ADR 0013). Stores the URL; no oEmbed request is made."""

    url = blocks.URLBlock(
        label=_("YouTube link"),
        help_text=_("e.g. https://www.youtube.com/watch?v=…"),
    )
    title = blocks.CharBlock(
        label=_("Title"), help_text=_("Shown before the video is loaded.")
    )

    class Meta:
        icon = "media"
        label = _("YouTube video")
        template = "stories/blocks/youtube.html"
        value_class = YouTubeValue

    def clean(self, value):
        value = super().clean(value)
        if not youtube_id(value.get("url")):
            raise StructBlockValidationError(
                block_errors={
                    "url": ValidationError(_("This is not a YouTube video link."))
                }
            )
        return value


class BookExcerptBlock(blocks.StructBlock):
    text = blocks.TextBlock(
        label=_("Excerpt"), help_text=_("A short quote only, not whole pages.")
    )
    book_title = blocks.CharBlock(label=_("Book title"))
    author = blocks.CharBlock(label=_("Author"))
    page = blocks.CharBlock(required=False, label=_("Page"))
    link = blocks.URLBlock(required=False, label=_("Link"))

    class Meta:
        icon = "doc-full"
        label = _("Book excerpt")
        template = "stories/blocks/book_excerpt.html"


class StoryBodyBlock(blocks.StreamBlock):
    paragraph = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul"], label=_("Paragraph")
    )
    heading = HeadingBlock()
    quote = QuoteBlock()
    image = StoryImageBlock()
    youtube = YouTubeBlock()
    book_excerpt = BookExcerptBlock()
