from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.models import DraftStateMixin, RevisionMixin

from core.geo import latitude_field, longitude_field
from core.themes import Theme


class PlaceQuerySet(models.QuerySet):
    def public(self):
        """Places shown on the site: published only."""
        return self.filter(live=True)


class Place(DraftStateMixin, RevisionMixin, models.Model):
    """A place of interest on the map (snippet with draft/publish)."""

    name = models.CharField(_("name"), max_length=200)
    theme = models.CharField(_("theme"), max_length=20, choices=Theme.choices)
    latitude = latitude_field()
    longitude = longitude_field()
    short_description = models.TextField(
        _("short description"),
        max_length=300,
        help_text=_("One or two sentences, shown on the map card."),
    )
    to_be_checked = models.BooleanField(
        _("to be checked"),
        default=False,
        help_text=_(
            "Tick while the coordinates or the description still need to be verified."
        ),
    )

    objects = PlaceQuerySet.as_manager()

    panels = [
        FieldPanel("name"),
        FieldPanel("theme"),
        FieldRowPanel([FieldPanel("latitude"), FieldPanel("longitude")]),
        FieldPanel("short_description"),
        FieldPanel("to_be_checked"),
    ]

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        ordering = ["name"]

    def __str__(self):
        return self.name
