"""Seed data for the local prototype (docs/PROJECT_BRIEF.md, section 5).

Creates the theme pages, five example places, three placeholder stories,
placeholder events and projects. Safe to run more than once: existing
objects are left alone. No invented facts: everything that is not verified
is in [square brackets] or marked "to be checked".
"""

import datetime
import io
from decimal import Decimal

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from PIL import Image as PILImage
from wagtail.images import get_image_model

from core.themes import Theme
from events.models import Event
from home.models import HomePage
from places.models import Place
from projects.models import Project, ProjectKind
from stories.models import StoryPage, ThemeIndexPage

TO_BE_CHECKED = "[To be checked]"

# Coordinates and descriptions must be verified by the editor before going
# live (issue #15); every place is flagged `to_be_checked`.
PLACES = [
    {
        "name": "Mount Ararat",
        "theme": Theme.SYMBOLS,
        "latitude": Decimal("39.701944"),
        "longitude": Decimal("44.298333"),
        "short_description": "The mountain at the heart of Armenian identity, "
        "visible from Yerevan; today it lies in Turkey.",
    },
    {
        "name": "Lake Sevan",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.316667"),
        "longitude": Decimal("45.350000"),
        "short_description": "A large high-altitude freshwater lake in the "
        "Gegharkunik province.",
    },
    {
        "name": "Garni Temple",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.112500"),
        "longitude": Decimal("44.730278"),
        "short_description": "A classical colonnaded temple above the Azat "
        "valley, near the village of Garni.",
    },
    {
        "name": "Geghard Monastery",
        "theme": Theme.MYTHS,
        "latitude": Decimal("40.140556"),
        "longitude": Decimal("44.818333"),
        "short_description": "A monastery partly carved into the rock of the "
        "upper Azat valley, named after a holy spear.",
    },
    {
        "name": "Gyumri",
        "theme": Theme.TRADITIONS,
        "latitude": Decimal("40.783333"),
        "longitude": Decimal("43.833333"),
        "short_description": "Armenia's second-largest city, in the Shirak province.",
    },
]

STORIES = [
    {"title": "The eternity sign", "theme": Theme.SYMBOLS, "places": []},
    {
        "title": "The duduk, voice of apricot wood",
        "theme": Theme.MUSIC,
        "places": [],
    },
    {
        "title": "The monastery of the spear",
        "theme": Theme.MYTHS,
        "places": ["Geghard Monastery"],
    },
]

PROJECTS = [
    ("[Project name 1]", ProjectKind.SHOP),
    ("[Project name 2]", ProjectKind.STARTUP),
    ("[Project name 3]", ProjectKind.CRAFTS),
    ("[Project name 4]", ProjectKind.MUSIC),
]

PLACEHOLDER_IMAGE_TITLE = "[Placeholder image]"


class Command(BaseCommand):
    help = "Create placeholder content for the local prototype."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Run even with DEBUG off (e.g. on a test server).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_production"]:
            raise CommandError(
                "DEBUG is off. Seed data is for local prototypes; pass "
                "--allow-production to run it anyway."
            )
        self.created = 0
        image = self.placeholder_image()
        places = {data["name"]: self.place(data) for data in PLACES}
        theme_pages = self.theme_pages()
        for data in STORIES:
            self.story(data, theme_pages[data["theme"]], image, places)
        for number in range(1, 4):
            self.event(number)
        for name, kind in PROJECTS:
            self.project(name, kind)
        self.stdout.write(
            self.style.SUCCESS(f"Seed data ready ({self.created} objects created).")
        )

    def publish(self, obj):
        obj.save_revision().publish()
        self.created += 1

    def placeholder_image(self):
        Image = get_image_model()
        image = Image.objects.filter(title=PLACEHOLDER_IMAGE_TITLE).first()
        if image:
            return image
        buffer = io.BytesIO()
        # Plain dark rectangle in the surface colour: no AI images, no symbols.
        PILImage.new("RGB", (1600, 900), "#161311").save(buffer, "PNG")
        image = Image.objects.create(
            title=PLACEHOLDER_IMAGE_TITLE,
            file=ImageFile(buffer, name="placeholder.png"),
            description="Placeholder: plain dark rectangle",
            credit="[Photo with source and usage rights]",
            licence="[Placeholder]",
        )
        self.created += 1
        return image

    def place(self, data):
        place = Place.objects.filter(name=data["name"]).first()
        if place:
            return place
        place = Place(
            **(
                data
                | {"short_description": f"{TO_BE_CHECKED} {data['short_description']}"}
            ),
            to_be_checked=True,
        )
        place.save()
        self.publish(place)
        return place

    def theme_pages(self):
        home = HomePage.objects.get()
        pages = {}
        for theme in Theme:
            page = ThemeIndexPage.objects.filter(theme=theme).first()
            if not page:
                page = ThemeIndexPage(
                    title=str(theme.label), theme=theme, intro="[Introduction]"
                )
                home.add_child(instance=page)
                self.publish(page)
            pages[theme] = page
        return pages

    def story(self, data, parent, image, places):
        if StoryPage.objects.child_of(parent).filter(title=data["title"]).exists():
            return
        story = StoryPage(
            title=data["title"],
            teaser="[Teaser: two lines on what the article is about.]",
            hero_image=image,
            body=[("paragraph", "<p>[Placeholder text]</p>")],
        )
        parent.add_child(instance=story)
        story.related_places.set([places[name] for name in data["places"]])
        story.sources.create(title="[Source title]", note="[Author, year]")
        self.publish(story)

    def event(self, number):
        title = f"[Event name {number}]"
        if Event.objects.filter(title=title).exists():
            return
        event = Event.objects.create(
            title=title,
            start_date=timezone.localdate() + datetime.timedelta(days=14 * number),
            city="[City]",
            country="[Country]",
            link="https://example.org/",
        )
        self.publish(event)

    def project(self, name, kind):
        if Project.objects.filter(name=name).exists():
            return
        project = Project.objects.create(
            name=name,
            kind=kind,
            city="[City]",
            country="[Country]",
            link="https://example.org/",
            short_description="[Short description]",
        )
        self.publish(project)
