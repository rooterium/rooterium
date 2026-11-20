from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from events.models import Event
from places.models import Place
from projects.models import Project
from stories.models import StoryPage, ThemeIndexPage


@override_settings(DEBUG=True)
class SeedDemoTests(TestCase):
    def seed(self):
        call_command("seed_demo", stdout=StringIO())

    def counts(self):
        return [
            m.objects.count()
            for m in (Place, ThemeIndexPage, StoryPage, Event, Project)
        ]

    def test_creates_the_seed_data_from_the_brief(self):
        self.seed()
        self.assertEqual(self.counts(), [5, 5, 3, 3, 4])

    def test_running_twice_creates_no_duplicates(self):
        self.seed()
        self.seed()
        self.assertEqual(self.counts(), [5, 5, 3, 3, 4])

    def test_places_are_flagged_to_be_checked(self):
        self.seed()
        for place in Place.objects.all():
            self.assertTrue(place.to_be_checked)
            self.assertTrue(place.short_description.startswith("[To be checked]"))

    def test_everything_is_published_and_visible(self):
        self.seed()
        self.assertEqual(Place.objects.public().count(), 5)
        self.assertEqual(Event.objects.upcoming().count(), 3)
        story = StoryPage.objects.get(title="The monastery of the spear")
        self.assertEqual(story.theme, "myths")
        self.assertEqual(
            list(story.related_places.values_list("name", flat=True)),
            ["Geghard Monastery"],
        )
        self.assertEqual(self.client.get(story.url).status_code, 200)

    @override_settings(DEBUG=False)
    def test_refuses_to_run_with_debug_off(self):
        with self.assertRaises(CommandError):
            self.seed()
        self.assertEqual(Place.objects.count(), 0)
