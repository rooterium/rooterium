import io
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from PIL import Image as PILImage

from core import example_content as content
from events.models import Event
from pages.models import Purpose, SimplePage
from places.models import Place
from projects.models import Project
from stories.models import StoryPage

COMMAND = "core.management.commands.load_example_content"


def jpeg():
    buffer = io.BytesIO()
    PILImage.new("RGB", (40, 30), "#806040").save(buffer, "JPEG")
    return buffer.getvalue()


def fake_info(file_name):
    licence = next(spec[1] for spec in content.IMAGES.values() if spec[0] == file_name)
    return {
        "url": "https://upload.example/x.jpg",
        "page": f"https://commons.example/{file_name}",
        "licence": licence,
        "artist": "Jane Doe",
    }


@override_settings(DEBUG=True)
class LoadExampleContentTests(TestCase):
    def load(self):
        with (
            mock.patch(f"{COMMAND}.commons_info", side_effect=fake_info),
            mock.patch(f"{COMMAND}.fetch", return_value=jpeg()),
        ):
            call_command("seed_demo", stdout=io.StringIO())
            call_command("load_example_content", stdout=io.StringIO())

    def test_replaces_placeholders_with_example_content(self):
        self.load()
        self.assertFalse(StoryPage.objects.filter(teaser__startswith="[").exists())
        self.assertEqual(StoryPage.objects.live().count(), len(content.STORIES))
        self.assertFalse(Event.objects.filter(title__startswith="[").exists())
        self.assertFalse(Project.objects.filter(name__startswith="[").exists())
        self.assertFalse(Place.objects.filter(name="Lake Sevan").exists())
        self.assertTrue(Place.objects.get(name="Sevanavank").to_be_checked)
        about = SimplePage.objects.get(purpose=Purpose.ABOUT)
        self.assertIn("How it works", about.body)

    def test_images_carry_author_licence_and_source(self):
        self.load()
        story = StoryPage.objects.get(title="The monastery of the spear")
        self.assertEqual(
            story.hero_image.credit, "Photo: Diego Delso / Wikimedia Commons"
        )
        self.assertEqual(story.hero_image.licence, "CC BY-SA 4.0")
        self.assertTrue(
            story.hero_image.source_url.startswith(
                "https://commons.wikimedia.org/wiki/File:"
            )
        )
        self.assertTrue(story.sources.exists())

    def test_running_twice_creates_nothing_new(self):
        self.load()
        counts = (StoryPage.objects.count(), Event.objects.count())
        self.load()
        self.assertEqual((StoryPage.objects.count(), Event.objects.count()), counts)

    def test_stories_written_by_the_editor_are_left_alone(self):
        self.load()
        story = StoryPage.objects.get(title="The eternity sign")
        story.teaser = "The editor's own teaser."
        story.save_revision().publish()
        self.load()
        story.refresh_from_db()
        self.assertEqual(story.teaser, "The editor's own teaser.")

    def test_changed_licence_stops_the_import(self):
        def changed(file_name):
            return fake_info(file_name) | {"licence": "All rights reserved"}

        with (
            mock.patch(f"{COMMAND}.commons_info", side_effect=changed),
            mock.patch(f"{COMMAND}.fetch", return_value=jpeg()),
        ):
            call_command("seed_demo", stdout=io.StringIO())
            with self.assertRaises(CommandError):
                call_command("load_example_content", stdout=io.StringIO())

    def test_photos_can_come_from_a_folder_without_downloading(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as folder:
            for key in content.IMAGES:
                Path(folder, f"{key}.jpg").write_bytes(jpeg())
            with (
                mock.patch(f"{COMMAND}.commons_info") as info,
                mock.patch(f"{COMMAND}.fetch") as fetch,
            ):
                call_command("seed_demo", stdout=io.StringIO())
                call_command(
                    "load_example_content",
                    images_dir=Path(folder),
                    stdout=io.StringIO(),
                )
        info.assert_not_called()
        fetch.assert_not_called()
        self.assertEqual(StoryPage.objects.live().count(), len(content.STORIES))

    def test_stories_sit_in_their_sections_and_categories(self):
        self.load()
        expected = {
            "The monastery of the spear": ("religion", None),
            "The duduk, voice of apricot wood": ("music", None),
            "The eternity sign": ("symbols", "Eternity and the sun"),
            "A temple older than Christianity in Armenia": ("history", None),
            "Khachkars, crosses carved in stone": ("symbols", "Cross and khachkar"),
            "Ararat, the mountain on the horizon": ("symbols", "Ararat"),
        }
        for title, (section, category) in expected.items():
            with self.subTest(title=title):
                story = StoryPage.objects.get(title=title)
                self.assertEqual(story.theme, section)
                self.assertEqual(story.category and story.category.title, category)
