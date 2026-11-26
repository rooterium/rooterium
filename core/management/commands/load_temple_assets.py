"""Load the temple images and videos into the database (ADR 0019).

    python manage.py load_temple_assets design/temple/web

Reads the web versions built by `design/temple/build_temple_assets.py`
(see `core/temple_assets.py` for which file goes where), creates or
updates them as Wagtail images and documents in the collection "Temple",
then fills the home page's and the section pages' temple fields.

- An image or document is found by its title; if the file in the folder
  differs from the stored one, the stored file is replaced.
- A page field is only filled when it is empty, so an image the editor
  chose in the admin stays. Missing section pages are skipped with a note
  (run `restructure_sections` first).
- Safe to run more than once. Like the other content commands it refuses
  to run with DEBUG off unless `--allow-production` is given.
"""

import io
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection
from wagtail.utils.file import hash_filelike

from core import temple_assets as assets
from core.revisions import latest_version, save_version
from home.models import HomePage
from stories.models import ThemeIndexPage


class Command(BaseCommand):
    help = "Load the temple images and videos from a folder of web versions."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=Path, help="e.g. design/temple/web")
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Run even with DEBUG off (e.g. on the test server).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_production"]:
            raise CommandError(
                "DEBUG is off; pass --allow-production to load the temple "
                "assets anyway."
            )
        self.folder = options["folder"]
        files = [spec[0] for spec in assets.IMAGES.values()]
        files += [spec[0] for spec in assets.VIDEOS.values()]
        missing = [name for name in files if not (self.folder / name).is_file()]
        if missing:
            raise CommandError(
                f"Missing in {self.folder}: {', '.join(missing)}. Build them "
                "with design/temple/build_temple_assets.py."
            )
        with transaction.atomic():
            self.collection = self.temple_collection()
            loaded = {
                "image": {
                    k: self.image(*spec, focus=assets.FOCUS.get(k))
                    for k, spec in assets.IMAGES.items()
                },
                "video": {k: self.video(*spec) for k, spec in assets.VIDEOS.items()},
            }
            self.fill(HomePage.objects.get(), assets.HOME_FIELDS, loaded)
            for theme, fields in assets.SECTION_FIELDS.items():
                page = ThemeIndexPage.objects.filter(theme=theme).first()
                if page is None:
                    self.stdout.write(f"  skipped: no section page for {theme.label}")
                    continue
                self.fill(page, fields, loaded)
        self.stdout.write(self.style.SUCCESS("Temple assets loaded."))

    def temple_collection(self):
        root = Collection.get_first_root_node()
        existing = root.get_children().filter(name=assets.COLLECTION).first()
        return existing or root.add_child(name=assets.COLLECTION)

    def read(self, file_name):
        data = (self.folder / file_name).read_bytes()
        return data, hash_filelike(io.BytesIO(data))

    def image(self, file_name, title, alt, credit, focus=None):
        Image = get_image_model()
        data, digest = self.read(file_name)
        image = Image.objects.filter(title=title).first()
        if image and image.get_file_hash() == digest:
            if focus and image.focal_point_x is None:
                self.set_focus(image, focus)
            return image
        if image:
            image.renditions.all().delete()
            image.file.delete(save=False)
            action = "replaced"
        else:
            image = Image(
                title=title,
                description=alt,
                credit=credit,
                licence=assets.LICENCE,
                collection=self.collection,
            )
            action = "image"
        image.file = ContentFile(data, name=file_name)
        image._set_image_file_metadata()
        image.save()
        if focus and image.focal_point_x is None:
            self.set_focus(image, focus)
        self.stdout.write(f"  {action}: {title}")
        return image

    def set_focus(self, image, focus):
        """A small focal point at the given fractions of width and height."""
        x, y = focus
        image.focal_point_x = round(image.width * x)
        image.focal_point_y = round(image.height * y)
        image.focal_point_width = image.focal_point_height = round(image.width / 10)
        image.save(
            update_fields=[
                "focal_point_x",
                "focal_point_y",
                "focal_point_width",
                "focal_point_height",
            ]
        )

    def video(self, file_name, title):
        Document = get_document_model()
        data, digest = self.read(file_name)
        document = Document.objects.filter(title=title).first()
        if document and document.get_file_hash() == digest:
            return document
        if document:
            document.file.delete(save=False)
            action = "replaced"
        else:
            document = Document(title=title, collection=self.collection)
            action = "video"
        document.file = ContentFile(data, name=file_name)
        document._set_document_file_metadata()
        document.save()
        self.stdout.write(f"  {action}: {title}")
        return document

    def fill(self, page, fields, loaded):
        # Start from the editor's draft if there is one, and never publish
        # it (core.revisions).
        version = latest_version(page)
        changed = []
        for field, (kind, key) in fields.items():
            if getattr(version, f"{field}_id") is None:
                setattr(version, field, loaded[kind][key])
                changed.append(field)
        if not changed:
            return
        save_version(version)
        self.stdout.write(f"  {version.title}: {', '.join(changed)}")
