"""Load the example content (core/example_content.py) for the test phase.

Takes the photos from `--images-dir` (files named `<key>.jpg`, see
`IMAGES`) or downloads them from Wikimedia Commons (licence checked against
the Commons API; Commons throttles scripted downloads, so a folder is the
reliable way on a server), then creates or updates places, theme intros,
stories, events and projects, and the About page. Replaces the
[placeholder] objects of `seed_demo`; objects the editor has written are
left alone. The example stories are always put in their section and
category (ADR 0018), even when their text is left alone. Safe to run more
than once.
"""

import datetime
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from wagtail.images import get_image_model

from core import example_content as content
from core.sections import category
from core.themes import Theme
from events.models import Event
from pages.models import Purpose, SimplePage
from places.models import Place
from projects.models import Project
from stories.models import StoryPage, ThemeIndexPage

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "Rooterium/1.0 (example content loader)"
# One of the standard thumbnail widths; other sizes are rate-limited.
DOWNLOAD_WIDTH = 1920


def fetch(url, attempts=6):
    """GET with a pause and retries: Wikimedia answers 429 to fast clients."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        time.sleep(2)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == attempts:
                raise
            time.sleep(int(error.headers.get("Retry-After") or 0) or 30 * attempt)
    raise AssertionError("unreachable")


def plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def commons_info(file_name):
    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{file_name}",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": str(DOWNLOAD_WIDTH),
    }
    data = json.loads(fetch(f"{API}?{urllib.parse.urlencode(params)}"))
    page = next(iter(data["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise CommandError(f"Not found on Commons: {file_name}")
    info = page["imageinfo"][0]
    meta = info["extmetadata"]
    return {
        "url": info.get("thumburl") or info["url"],
        "page": info["descriptionurl"],
        "licence": plain(meta.get("LicenseShortName", {}).get("value")),
        "artist": plain(meta.get("Artist", {}).get("value")),
    }


def is_placeholder(text):
    return (text or "").lstrip().startswith(("[", "<p>["))


class Command(BaseCommand):
    help = "Load the example content with real photos (test phase)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Run even with DEBUG off (e.g. on the test server).",
        )
        parser.add_argument(
            "--images-dir",
            type=Path,
            help="Folder with the photos as <key>.jpg (instead of downloading).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_production"]:
            raise CommandError(
                "DEBUG is off. Example content is for the test phase; pass "
                "--allow-production to run it anyway."
            )
        self.images_dir = options["images_dir"]
        images = {key: self.image(key, *spec) for key, spec in content.IMAGES.items()}
        with transaction.atomic():
            places = {data["name"]: self.place(data) for data in content.PLACES}
            theme_pages = self.theme_pages()
            for data in content.STORIES:
                parent = theme_pages[data["theme"]]
                if data.get("category"):
                    parent = category(data["theme"], data["category"])
                    if parent is None:
                        raise CommandError(
                            f"Category {data['category']} missing: run "
                            "restructure_sections first."
                        )
                self.story(data, parent, images, places)
            self.events()
            self.projects()
            self.about()
        self.stdout.write(self.style.SUCCESS("Example content loaded."))

    def publish(self, obj, what):
        obj.save_revision().publish()
        self.stdout.write(f"  {what}: {obj}")

    # --- Images ------------------------------------------------------------

    def image(self, key, file_name, licence, artist, alt):
        Image = get_image_model()
        title = file_name.rsplit(".", 1)[0]
        existing = Image.objects.filter(title=title).first()
        if existing:
            return existing
        local = self.images_dir / f"{key}.jpg" if self.images_dir else None
        if local and local.is_file():
            data = local.read_bytes()
        else:
            info = commons_info(file_name)
            if info["licence"] != licence:
                raise CommandError(
                    f"{file_name}: licence on Commons is now {info['licence']!r}, "
                    f"expected {licence!r}. Check before using it."
                )
            data = fetch(info["url"])
        page = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(
            file_name.replace(" ", "_")
        )
        image = Image.objects.create(
            title=title,
            file=ContentFile(data, name=f"{key}.jpg"),
            description=alt,
            credit=f"Photo: {artist} / Wikimedia Commons",
            licence=licence,
            source_url=page,
        )
        self.stdout.write(f"  image: {title} ({licence}, {artist})")
        return image

    # --- Places and theme pages ------------------------------------------

    def place(self, data):
        old_name = next(
            (old for old, new in content.RENAMED_PLACES.items() if new == data["name"]),
            None,
        )
        place = (
            Place.objects.filter(name=data["name"]).first()
            or Place.objects.filter(name=old_name).first()
        )
        if place and not place.to_be_checked:
            return place  # the editor has checked or written it
        place = place or Place()
        for field, value in data.items():
            setattr(place, field, value)
        # Facts from the listed sources, but the editor still confirms them.
        place.to_be_checked = True
        place.save()
        self.publish(place, "place")
        return place

    def theme_pages(self):
        pages = {}
        for theme in Theme:
            page = ThemeIndexPage.objects.filter(theme=theme).first()
            if not page:
                raise CommandError(
                    "Section pages missing: run restructure_sections (or "
                    "seed_demo) first."
                )
            if (
                not page.intro
                or is_placeholder(page.intro)
                or page.intro in content.LEGACY_THEME_INTROS
            ):
                page.intro = content.THEME_INTROS[theme]
                self.publish(page, "theme intro")
            pages[theme] = page
        return pages

    # --- Stories -----------------------------------------------------------

    def body(self, blocks, images):
        stream = []
        for block in blocks:
            kind = block[0]
            if kind == "paragraph":
                stream.append(("paragraph", block[1]))
            elif kind == "heading":
                stream.append(("heading", {"text": block[1], "level": "h2"}))
            elif kind == "image":
                stream.append(
                    ("image", {"image": images[block[1]], "caption": block[2]})
                )
        return stream

    def story(self, data, parent, images, places):
        story = StoryPage.objects.filter(title=data["title"]).first()
        if story:
            story = story.specific
            if story.get_parent().pk != parent.pk:
                story.move(parent, pos="last-child")
                story = StoryPage.objects.get(pk=story.pk)
                self.stdout.write(f"  moved to {parent.title}: {story}")
            if not is_placeholder(story.teaser):
                return  # written by the editor
        else:
            story = StoryPage(title=data["title"])
        story.teaser = data["teaser"]
        story.hero_image = images[data["hero"]]
        story.date = timezone.localdate() - datetime.timedelta(days=data["days_ago"])
        story.body = self.body(data["body"], images)
        if not story.pk:
            parent.add_child(instance=story)
        story.related_places.set([places[name] for name in data["places"]])
        story.sources.all().delete()
        for title, url, note in data["sources"]:
            story.sources.create(title=title, url=url, note=note)
        self.publish(story, "story")

    # --- Events, projects, About ------------------------------------------

    def events(self):
        for event in Event.objects.filter(title__startswith="["):
            event.delete()
        for data in content.EVENTS:
            if Event.objects.filter(title=data["title"]).exists():
                continue
            coords = data["coords"] or (None, None)
            event = Event.objects.create(
                title=data["title"],
                start_date=data["start_date"],
                city=data["city"],
                country=data["country"],
                link=data["link"],
                latitude=coords[0],
                longitude=coords[1],
            )
            self.publish(event, "event")

    def projects(self):
        for project in Project.objects.filter(name__startswith="["):
            project.delete()
        for data in content.PROJECTS:
            if Project.objects.filter(name=data["name"]).exists():
                continue
            project = Project.objects.create(**data)
            self.publish(project, "project")

    def about(self):
        page = SimplePage.objects.filter(purpose=Purpose.ABOUT).first()
        if not page or not is_placeholder(page.body):
            return
        page.intro = (
            "Armenian history, traditions, myths, symbols and music, "
            "collected and connected."
        )
        page.body = content.ABOUT_BODY
        self.publish(page, "page")
