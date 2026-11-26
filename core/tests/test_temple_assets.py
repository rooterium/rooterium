import io
import tempfile
from pathlib import Path

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from PIL import Image as PILImage
from wagtail.documents import get_document_model
from wagtail.images import get_image_model

from core import temple_assets as assets
from core.sections import ensure_sections
from core.themes import Theme
from home.models import HomePage
from images.testing import make_image
from stories.models import ThemeIndexPage


def webp(colour="#302820"):
    buffer = io.BytesIO()
    PILImage.new("RGB", (32, 18), colour).save(buffer, "WEBP")
    return buffer.getvalue()


@override_settings(DEBUG=True)
class LoadTempleAssetsTests(TestCase):
    def setUp(self):
        ensure_sections()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        for file_name, *_ in assets.IMAGES.values():
            (self.folder / file_name).write_bytes(webp())
        for file_name, _ in assets.VIDEOS.values():
            (self.folder / file_name).write_bytes(
                b"\x00\x00\x00\x18ftypmp42 test video"
            )

    def load(self, *args):
        call_command(
            "load_temple_assets", str(self.folder), *args, stdout=io.StringIO()
        )

    def test_creates_images_videos_and_fills_the_pages(self):
        self.load()
        Image, Document = get_image_model(), get_document_model()
        self.assertEqual(Image.objects.filter(title__startswith="Temple:").count(), 8)
        self.assertEqual(
            Document.objects.filter(title__startswith="Temple:").count(), 3
        )
        portal = Image.objects.get(title="Temple: portal")
        self.assertEqual(portal.credit, assets.CREDIT_STILL)
        self.assertEqual(portal.licence, assets.LICENCE)
        self.assertTrue(portal.description)
        self.assertEqual(portal.collection.name, "Temple")
        home = HomePage.objects.get()
        self.assertEqual(home.portal_poster, portal)
        self.assertEqual(home.entrance_video.title, "Temple: entrance")
        self.assertTrue(home.entrance_video.url.startswith("/media/documents/"))
        symbols = ThemeIndexPage.objects.get(theme=Theme.SYMBOLS)
        self.assertEqual(symbols.hall_image.title, "Temple: Symbols hall")
        self.assertEqual(symbols.descent_video.title, "Temple: descent into Symbols")
        music = ThemeIndexPage.objects.get(theme=Theme.MUSIC)
        self.assertIsNone(music.descent_video)
        self.assertFalse(home.has_unpublished_changes)

    def test_running_twice_creates_nothing_new(self):
        self.load()
        self.load()
        self.assertEqual(
            get_image_model().objects.filter(title__startswith="Temple:").count(), 8
        )
        self.assertEqual(get_document_model().objects.count(), 3)

    def test_changed_file_replaces_the_stored_one(self):
        self.load()
        portal = get_image_model().objects.get(title="Temple: portal")
        old_hash = portal.file_hash
        (self.folder / assets.IMAGES["portal"][0]).write_bytes(webp("#a6352c"))
        self.load()
        portal.refresh_from_db()
        self.assertNotEqual(portal.file_hash, old_hash)
        self.assertEqual(
            get_image_model().objects.filter(title="Temple: portal").count(), 1
        )

    def test_image_chosen_by_the_editor_stays(self):
        chosen = make_image()
        music = ThemeIndexPage.objects.get(theme=Theme.MUSIC)
        music.hall_image = chosen
        music.save_revision().publish()
        self.load()
        music.refresh_from_db()
        self.assertEqual(music.hall_image, chosen)

    def test_missing_file_stops_before_changing_anything(self):
        (self.folder / assets.VIDEOS["entrance"][0]).unlink()
        with self.assertRaises(CommandError):
            self.load()
        self.assertFalse(
            get_image_model().objects.filter(title__startswith="Temple:").exists()
        )

    @override_settings(DEBUG=False)
    def test_refuses_to_run_with_debug_off(self):
        with self.assertRaises(CommandError):
            self.load()
        self.load("--allow-production")
        self.assertIsNotNone(HomePage.objects.get().chapel_image)


class EditorDocumentPermissionTests(TestCase):
    def test_editors_can_upload_documents(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        from wagtail.documents.permissions import permission_policy

        editor = get_user_model().objects.create_user("ed", password="x", is_staff=True)
        editor.groups.add(Group.objects.get(name="Editors"))
        self.assertTrue(permission_policy.user_has_permission(editor, "add"))
        self.assertTrue(permission_policy.user_has_permission(editor, "choose"))
