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


@mock.patch("events.models.timezone.localdate", return_value=TODAY)
class EventListPageTests(TestCase):
    def test_shows_upcoming_events_only(self, _):
        make_event(title="[Upcoming]", start_date=TODAY + datetime.timedelta(days=3))
        make_event(title="[Past]", start_date=TODAY - datetime.timedelta(days=1))
        make_event(title="[Draft]", live=False)
        response = self.client.get("/events/")
        self.assertContains(response, "<title>Events – Rooterium</title>", html=True)
        self.assertContains(response, '<meta name="description" content="Upcoming')
        self.assertContains(response, "[Upcoming]")
        self.assertNotContains(response, "[Past]")
        self.assertNotContains(response, "[Draft]")

    def test_multi_day_event_shows_its_date_range(self, _):
        make_event(start_date=TODAY, end_date=datetime.date(2026, 11, 22))
        response = self.client.get("/events/")
        self.assertContains(response, "20 Nov 2026")
        self.assertContains(response, "22 Nov 2026")

    def test_map_link_only_for_events_with_coordinates(self, _):
        on_map = make_event(latitude=Decimal("40.18"), longitude=Decimal("44.51"))
        make_event(title="[Without position]")
        response = self.client.get("/events/")
        self.assertContains(response, f'href="/?place=event-{on_map.pk}#explore"')
        self.assertContains(response, "Show on the map", count=1)

    def test_empty_list(self, _):
        self.assertContains(
            self.client.get("/events/"), "No upcoming events at the moment."
        )

    def test_main_navigation_and_home_page_link_to_events(self, _):
        self.assertContains(
            self.client.get("/events/"),
            '<a href="/events/" aria-current="page">Events</a>',
            html=True,
        )
        self.assertContains(self.client.get("/"), 'href="/events/"')
