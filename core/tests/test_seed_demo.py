from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from events.models import Event
from pages.models import SimplePage
from places.models import Place
from projects.models import Project
from stories.models import CategoryPage, StoryPage, ThemeIndexPage


@override_settings(DEBUG=True)
class SeedDemoTests(TestCase):
    def seed(self):
        call_command("seed_demo", stdout=StringIO())

    def counts(self):
        return [
            m.objects.count()
            for m in (
                Place,
                ThemeIndexPage,
                CategoryPage,
                StoryPage,
                Event,
                Project,
                SimplePage,
            )
        ]

    def test_creates_the_seed_data_from_the_brief(self):
        self.seed()
        self.assertEqual(self.counts(), [5, 6, 8, 3, 3, 4, 3])

    def test_running_twice_creates_no_duplicates(self):
        self.seed()
        self.seed()
        self.assertEqual(self.counts(), [5, 6, 8, 3, 3, 4, 3])

    def test_stories_sit_in_their_section_and_category(self):
        self.seed()
        sign = StoryPage.objects.get(title="The eternity sign")
        self.assertEqual(sign.get_parent().title, "Eternity and the sun")
        self.assertEqual(sign.theme, "symbols")

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
        self.assertEqual(story.theme, "religion")
        self.assertEqual(
            list(story.related_places.values_list("name", flat=True)),
            ["Geghard Monastery"],
        )
        self.assertEqual(self.client.get(story.url).status_code, 200)

    def test_stories_get_a_story_shaped_placeholder_body(self):
        self.seed()
        story = StoryPage.objects.get(title="The eternity sign")
        types = [block.block_type for block in story.body]
        for block_type in ("paragraph", "heading", "quote", "image", "book_excerpt"):
            self.assertIn(block_type, types)
        response = self.client.get(story.url)
        self.assertContains(response, "[First section heading]")
        self.assertContains(response, "[Book title]")

    def test_old_one_line_bodies_are_upgraded_but_edited_ones_kept(self):
        self.seed()
        old = StoryPage.objects.get(title="The eternity sign")
        old.body = [("paragraph", "<p>[Placeholder text]</p>")]
        old.save_revision().publish()
        edited = StoryPage.objects.get(title="The duduk, voice of apricot wood")
        edited.body = [("paragraph", "<p>Real text by the editor.</p>")]
        edited.save_revision().publish()
        self.seed()
        old.refresh_from_db()
        edited.refresh_from_db()
        self.assertGreater(len(old.body), 5)
        self.assertEqual(len(edited.body), 1)
        self.assertIn("Real text by the editor.", str(edited.body))

    @override_settings(DEBUG=False)
    def test_refuses_to_run_with_debug_off(self):
        with self.assertRaises(CommandError):
            self.seed()
        self.assertEqual(Place.objects.count(), 0)
