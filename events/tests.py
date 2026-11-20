import datetime
from decimal import Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from events.models import Event

TODAY = datetime.date(2026, 11, 20)


def make_event(**kwargs):
    defaults = {
        "title": "[Event name]",
        "start_date": TODAY,
        "city": "[City]",
        "country": "[Country]",
        "link": "https://example.org/",
    }
    return Event.objects.create(**(defaults | kwargs))


@mock.patch("events.models.timezone.localdate", return_value=TODAY)
class UpcomingEventsTests(TestCase):
    def test_past_events_disappear(self, _):
        make_event(title="Yesterday", start_date=TODAY - datetime.timedelta(days=1))
        self.assertFalse(Event.objects.upcoming().exists())

    def test_todays_and_future_events_are_shown_in_date_order(self, _):
        later = make_event(title="Later", start_date=TODAY + datetime.timedelta(days=5))
        today = make_event(title="Today")
        self.assertQuerySetEqual(Event.objects.upcoming(), [today, later])

    def test_ongoing_multi_day_event_is_shown(self, _):
        event = make_event(
            start_date=TODAY - datetime.timedelta(days=2),
            end_date=TODAY + datetime.timedelta(days=1),
        )
        self.assertQuerySetEqual(Event.objects.upcoming(), [event])

    def test_drafts_are_not_shown(self, _):
        make_event(live=False)
        self.assertFalse(Event.objects.upcoming().exists())


class EventValidationTests(TestCase):
    def event(self, **kwargs):
        defaults = {
            "title": "x",
            "start_date": TODAY,
            "city": "x",
            "country": "x",
            "link": "https://example.org/",
        }
        return Event(**(defaults | kwargs))

    def test_end_date_before_start_date_is_invalid(self):
        event = self.event(end_date=TODAY - datetime.timedelta(days=1))
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("end_date", cm.exception.message_dict)

    def test_coordinates_need_both_values(self):
        event = self.event(latitude=Decimal("40.1"))
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("longitude", cm.exception.message_dict)

    def test_without_coordinates_is_valid(self):
        self.event().full_clean()
