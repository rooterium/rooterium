from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.models import DraftStateMixin, RevisionMixin

from core.geo import latitude_field, longitude_field


class EventQuerySet(models.QuerySet):
    def upcoming(self):
        """Published events whose last day is today or later (Vienna time)."""
        today = timezone.localdate()
        return self.filter(live=True).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today)
        )


class Event(DraftStateMixin, RevisionMixin, models.Model):
    """An event (snippet with draft/publish). Past events disappear."""

    title = models.CharField(_("title"), max_length=200)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(
        _("end date"), null=True, blank=True, help_text=_("Only for multi-day events.")
    )
    city = models.CharField(_("city"), max_length=100)
    country = models.CharField(_("country"), max_length=100)
    link = models.URLField(_("link"), help_text=_("Page with details or tickets."))
    latitude = latitude_field(null=True, blank=True)
    longitude = longitude_field(null=True, blank=True)
    submitted_by_email = models.EmailField(
        _("submitted by (email)"),
        blank=True,
        help_text=_("Only for contacting the submitter. Never shown publicly."),
    )

    objects = EventQuerySet.as_manager()

    panels = [
        FieldPanel("title"),
        FieldRowPanel([FieldPanel("start_date"), FieldPanel("end_date")]),
        FieldRowPanel([FieldPanel("city"), FieldPanel("country")]),
        FieldPanel("link"),
        MultiFieldPanel(
            [FieldRowPanel([FieldPanel("latitude"), FieldPanel("longitude")])],
            heading=_("Position on the map (optional)"),
        ),
        FieldPanel("submitted_by_email"),
    ]

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["start_date", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = _("The end date cannot be before the start date.")
        if (self.latitude is None) != (self.longitude is None):
            errors["longitude" if self.longitude is None else "latitude"] = _(
                "Enter both latitude and longitude, or neither."
            )
        if errors:
            raise ValidationError(errors)
