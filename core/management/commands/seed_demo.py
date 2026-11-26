"""Seed data for the local prototype (docs/PROJECT_BRIEF.md, section 5).

Creates the six section pages and the Symbols categories
(`core.sections.ensure_sections`), five example places, three placeholder
stories,
placeholder events and projects, and placeholder About, Imprint and Privacy
pages (the real texts come from the editor, issue #14). Safe to run more than once: existing
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

from core.sections import category, ensure_sections
from core.themes import Theme
from events.models import Event
from home.models import HomePage
from pages.models import Purpose, SimplePage
from places.models import Place
from projects.models import Project, ProjectKind
from stories.models import StoryPage

TO_BE_CHECKED = "[To be checked]"

# Placeholders only: the editor writes the real texts (issue #14). The
# privacy notes list what the code actually does, as a starting point.
TEXT_PAGES = [
    {
        "purpose": Purpose.ABOUT,
        "title": "About",
        "slug": "about",
        "intro": "[One or two sentences: what Rooterium is and who it is for]",
        "body": (
            "<p>[Placeholder – the editor writes this text.]</p>"
            "<h2>[Why Rooterium]</h2><p>[The idea behind the project]</p>"
            "<h2>[Who is behind it]</h2><p>[The editor, the team]</p>"
            "<h2>[Contact]</h2><p>[How to get in touch]</p>"
        ),
    },
    {
        "purpose": Purpose.IMPRINT,
        "title": "Imprint",
        "slug": "imprint",
        "intro": "",
        "body": (
            "<p>[Placeholder – the editor provides the legally required "
            "details (Austrian disclosure rules); to be checked.]</p>"
            "<h2>[Media owner and publisher]</h2>"
            "<p>[Name]<br/>[Place of residence or address]</p>"
            "<h2>[Contact]</h2><p>[Email address]</p>"
            "<h2>[Purpose of the website]</h2><p>[Basic direction]</p>"
        ),
    },
    {
        "purpose": Purpose.PRIVACY,
        "title": "Privacy",
        "slug": "privacy",
        "intro": "",
        "body": (
            "<p>[Placeholder – the editor provides the privacy policy; to "
            "be checked. Technical facts as a starting point:]</p>"
            "<h2>[Controller]</h2><p>[Name, contact]</p>"
            "<h2>[Visiting the website]</h2><p>[No analytics, no "
            "advertising, no third-party scripts. Fonts and map tiles are "
            "served by this website itself. The only cookie is the "
            "technically necessary security cookie for forms (CSRF). Server "
            "logs: to be described with the hosting provider.]</p>"
            "<h2>[YouTube videos]</h2><p>[Loaded from youtube-nocookie.com "
            "only after a click on the video.]</p>"
            "<h2>[Newsletter]</h2><p>[Email address, the consent text and "
            "the time of consent and confirmation are stored (double "
            "opt-in). Unconfirmed sign-ups are deleted after 7 days; "
            "unsubscribing deletes the address. Email service: to be "
            "decided.]</p>"
            "<h2>[Suggesting an event or a project]</h2><p>[The email "
            "address is stored with the suggestion, only for questions "
            "about it, and never shown publicly.]</p>"
            "<h2>[Your rights]</h2><p>[Access, rectification, erasure, "
            "complaint to the Austrian data protection authority]</p>"
        ),
    },
]

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
        "theme": Theme.RELIGION,
        "latitude": Decimal("40.140556"),
        "longitude": Decimal("44.818333"),
        "short_description": "A monastery partly carved into the rock of the "
        "upper Azat valley, named after a holy spear.",
    },
    {
        "name": "Gyumri",
        "theme": Theme.HISTORY,
        "latitude": Decimal("40.783333"),
        "longitude": Decimal("43.833333"),
        "short_description": "Armenia's second-largest city, in the Shirak province.",
    },
]

# "category": slug of a category page in the section (core/sections.py).
STORIES = [
    {
        "title": "The eternity sign",
        "theme": Theme.SYMBOLS,
        "category": "eternity-and-the-sun",
        "places": [],
    },
    {
        "title": "The duduk, voice of apricot wood",
        "theme": Theme.MUSIC,
        "places": [],
    },
    {
        "title": "The monastery of the spear",
        "theme": Theme.RELIGION,
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

# The one-line body of earlier seed runs; such stories get the full
# placeholder body below. Stories with any other body are left alone.
OLD_PLACEHOLDER_BODY = "<p>[Placeholder text]</p>"


def placeholder_body(image):
    """A story-shaped placeholder: every text block type, realistic lengths,
    no invented facts (everything in [brackets])."""
    para = (
        "<p>[Placeholder paragraph – {what}. Three to five sentences of "
        "plain, warm language for readers who grew up far from Armenia. "
        "Names, dates and places only from the sources listed below.]</p>"
    )
    return [
        (
            "paragraph",
            para.format(
                what="the opening: a place, a moment or a "
                "question that draws the reader in"
            ),
        ),
        (
            "paragraph",
            para.format(
                what="why this matters to Armenians "
                "today, in Armenia and in the diaspora"
            ),
        ),
        ("heading", {"text": "[First section heading]", "level": "h2"}),
        (
            "paragraph",
            para.format(
                what="the history: what is known, and where the sources disagree"
            ),
        ),
        (
            "quote",
            {
                "text": "[A short quote from a source – a line from a song, a "
                "saying or a historical text.]",
                "source": "[Who said or wrote it]",
                "source_url": "",
            },
        ),
        ("paragraph", para.format(what="the story or legend as it is told")),
        (
            "image",
            {
                "image": image,
                "caption": "[Caption: what the photo shows, where and when]",
            },
        ),
        ("heading", {"text": "[Second section heading]", "level": "h2"}),
        (
            "paragraph",
            para.format(
                what="how the tradition lives on: "
                "customs, music, crafts, family memories"
            ),
        ),
        (
            "book_excerpt",
            {
                "text": "[A short excerpt from a book – two or three sentences, "
                "never whole pages.]",
                "book_title": "[Book title]",
                "author": "[Author]",
                "page": "[Page]",
                "link": "",
            },
        ),
        ("heading", {"text": "[Subheading]", "level": "h3"}),
        (
            "paragraph",
            para.format(
                what="the closing: an invitation to "
                "visit the place, listen or ask the family"
            ),
        ),
    ]


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
        sections = ensure_sections()
        for data in STORIES:
            parent = sections[data["theme"]]
            if data.get("category"):
                parent = category(data["theme"], data["category"])
            self.story(data, parent, image, places)
        for number in range(1, 4):
            self.event(number)
        for name, kind in PROJECTS:
            self.project(name, kind)
        for data in TEXT_PAGES:
            self.text_page(data)
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

    def text_page(self, data):
        if SimplePage.objects.filter(purpose=data["purpose"]).exists():
            return
        page = SimplePage(**data)
        HomePage.objects.get().add_child(instance=page)
        self.publish(page)

    def story(self, data, parent, image, places):
        # By title anywhere: the story may have been moved (e.g. into a
        # category by restructure_sections or load_example_content).
        existing = StoryPage.objects.filter(title=data["title"])
        if existing.exists():
            story = existing.first().specific
            if story.body.raw_data and [
                (b["type"], b["value"]) for b in story.body.raw_data
            ] == [("paragraph", OLD_PLACEHOLDER_BODY)]:
                story.body = placeholder_body(image)
                self.publish(story)
            return
        story = StoryPage(
            title=data["title"],
            teaser="[Teaser: two lines on what the article is about.]",
            hero_image=image,
            body=placeholder_body(image),
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
