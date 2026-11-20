"""Shared coordinate fields (ADR 0014: decimals with six places)."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


def latitude_field(**kwargs):
    return models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text=_("Decimal degrees, north is positive, e.g. 40.177200."),
        **kwargs,
    )


def longitude_field(**kwargs):
    return models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text=_("Decimal degrees, east is positive, e.g. 44.503490."),
        **kwargs,
    )
