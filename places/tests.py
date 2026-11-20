from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.themes import Theme
from places.models import Place


def make_place(**kwargs):
    defaults = {
        "name": "Garni Temple",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.112500"),
        "longitude": Decimal("44.730000"),
        "short_description": "[Short description]",
    }
    return Place.objects.create(**(defaults | kwargs))


class PlaceTests(TestCase):
    def test_public_shows_only_published_places(self):
        live = make_place(name="Live")
        make_place(name="Draft", live=False)
        self.assertQuerySetEqual(Place.objects.public(), [live])

    def test_latitude_out_of_range_is_invalid(self):
        place = Place(
            name="Nowhere",
            theme=Theme.MYTHS,
            latitude=Decimal("91"),
            longitude=Decimal("44"),
            short_description="x",
        )
        with self.assertRaises(ValidationError) as cm:
            place.full_clean()
        self.assertIn("latitude", cm.exception.message_dict)
