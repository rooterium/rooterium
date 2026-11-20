"""Image model with required alt text, credit and licence (ADR 0014)."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
    # Wagtail's own description field is its default alt text
    # (`default_alt_text`, ImageBlock); here it is required and labelled so.
    description = models.CharField(
        _("alt text"),
        max_length=255,
        help_text=_(
            "Describe what the image shows for people who cannot see it, "
            'e.g. "Snow-covered Mount Ararat above the Ararat plain".'
        ),
    )
    credit = models.CharField(
        _("credit"),
        max_length=250,
        help_text=_('Shown under the image, e.g. "Photo: Jane Doe".'),
    )
    licence = models.CharField(
        _("licence"),
        max_length=250,
        help_text=_(
            'Usage rights, e.g. "CC BY-SA 4.0", "With written permission" or '
            '"Own photo".'
        ),
    )
    source_url = models.URLField(
        _("source URL"),
        blank=True,
        help_text=_("Where the image comes from, if it is from the web."),
    )

    admin_form_fields = (
        *Image.admin_form_fields,
        "credit",
        "licence",
        "source_url",
    )

    class Meta(AbstractImage.Meta):
        verbose_name = _("image")
        verbose_name_plural = _("images")


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
