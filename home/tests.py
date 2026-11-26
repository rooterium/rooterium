from django.test import TestCase
from wagtail.models import Site

from core.themes import Theme
from home.models import HomePage
from places.tests import make_place


class HomePageSetupTests(TestCase):
    def test_home_page_is_the_default_site_root(self):
        site = Site.objects.get(is_default_site=True)
        self.assertIsInstance(site.root_page.specific, HomePage)

    def test_only_one_home_page_allowed(self):
        self.assertEqual(HomePage.max_count, 1)


class HomeMapTests(TestCase):
    def setUp(self):
        import datetime
        from decimal import Decimal

        from core.themes import Theme
        from events.models import Event
        from places.tests import make_place
        from stories.models import ThemeIndexPage
        from stories.tests import make_story

        self.home = HomePage.objects.get()
        religion = ThemeIndexPage(title="Religion", theme=Theme.RELIGION)
        self.home.add_child(instance=religion)
        self.place = make_place(name="Geghard Monastery", theme=Theme.RELIGION)
        make_place(name="[Draft place]", live=False)
        self.story = make_story(religion, title="The monastery of the spear")
        self.story.related_places.add(self.place)
        self.story.save_revision().publish()
        Event.objects.create(
            title="[Event with coordinates]",
            start_date=datetime.date.today() + datetime.timedelta(days=3),
            city="[City]",
            country="[Country]",
            link="https://example.org/",
            latitude=Decimal("40.1"),
            longitude=Decimal("44.5"),
        )

    def features(self, response):
        return response.context["map_features"]

    def test_markers_are_live_places_and_events_with_coordinates(self):
        names = [f["name"] for f in self.features(self.client.get("/"))]
        self.assertIn("Geghard Monastery", names)
        self.assertIn("[Event with coordinates]", names)
        self.assertNotIn("[Draft place]", names)

    def test_place_marker_links_to_its_story(self):
        feature = next(
            f
            for f in self.features(self.client.get("/"))
            if f["name"] == "Geghard Monastery"
        )
        self.assertEqual(feature["url"], self.story.url)
        self.assertEqual(feature["category"], "religion")
        self.assertEqual(feature["categoryLabel"], "Religion")

    def test_data_is_embedded_as_json_and_list_fallback_is_rendered(self):
        response = self.client.get("/")
        self.assertContains(
            response, '<script id="map-features" type="application/json">'
        )
        self.assertContains(response, "All places as a list")
        self.assertContains(response, "<strong>Geghard Monastery</strong>", html=True)

    def test_filters_include_themes_events_and_projects(self):
        response = self.client.get("/")
        for value in ("all", "history", "religion", "events", "projects"):
            self.assertContains(response, f'data-filter="{value}"')

    def test_without_tile_file_the_map_has_no_tiles(self):
        with self.settings(MEDIA_ROOT="/nonexistent"):
            response = self.client.get("/")
        self.assertContains(response, 'data-tiles=""')

    def test_with_tile_file_its_url_is_passed(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as media:
            Path(media, "maps").mkdir()
            Path(media, "maps", "rooterium.pmtiles").write_bytes(b"x")
            with self.settings(MEDIA_ROOT=media):
                response = self.client.get("/")
            self.assertContains(response, 'data-terrain=""')
            Path(media, "maps", "terrain.pmtiles").write_bytes(b"x")
            with self.settings(MEDIA_ROOT=media):
                with_terrain = self.client.get("/")
        self.assertContains(response, 'data-tiles="/media/maps/rooterium.pmtiles"')
        self.assertContains(with_terrain, 'data-terrain="/media/maps/terrain.pmtiles"')

    def test_latest_stories_events_and_projects_sections(self):
        response = self.client.get("/")
        self.assertContains(response, "Latest stories")
        self.assertContains(response, "The monastery of the spear")
        self.assertContains(response, "Upcoming events")
        self.assertContains(response, "Projects we love")


class HomeLayoutTests(TestCase):
    """Layout of the variant B mockup (design/mockup-2b-map.png)."""

    def test_heading_newsletter_band_and_suggest_links(self):
        response = self.client.get("/")
        self.assertContains(
            response, '<h1 id="explore-heading">Every root has a place.</h1>', html=True
        )
        self.assertContains(response, 'class="signup-form signup-form--inline"')
        self.assertContains(response, 'href="/suggest/event/"')
        self.assertContains(response, 'href="/suggest/project/"')


class MapPageTests(TestCase):
    """The map moved from the home page to /map/ (ADR 0017)."""

    def test_map_page_renders_the_map_module(self):
        place = make_place(name="Geghard Monastery", theme=Theme.RELIGION)
        response = self.client.get("/map/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Map – Rooterium</title>", html=True)
        self.assertContains(response, 'id="map-features"')
        self.assertContains(response, "data-map")
        self.assertContains(response, place.name)
        self.assertContains(response, "core/js/map.js")
        for value in Theme.values:
            self.assertContains(response, f'data-filter="{value}"')
