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


class MapDataTests(TestCase):
    """The map module's data, on /map/ since the temple redesign."""

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
        names = [f["name"] for f in self.features(self.client.get("/map/"))]
        self.assertIn("Geghard Monastery", names)
        self.assertIn("[Event with coordinates]", names)
        self.assertNotIn("[Draft place]", names)

    def test_place_marker_links_to_its_story(self):
        feature = next(
            f
            for f in self.features(self.client.get("/map/"))
            if f["name"] == "Geghard Monastery"
        )
        self.assertEqual(feature["url"], self.story.url)
        self.assertEqual(feature["category"], "religion")
        self.assertEqual(feature["categoryLabel"], "Religion")

    def test_data_is_embedded_as_json_and_list_fallback_is_rendered(self):
        response = self.client.get("/map/")
        self.assertContains(
            response, '<script id="map-features" type="application/json">'
        )
        self.assertContains(response, "All places as a list")
        self.assertContains(response, "<strong>Geghard Monastery</strong>", html=True)

    def test_filters_include_themes_events_and_projects(self):
        response = self.client.get("/map/")
        for value in ("all", "history", "religion", "events", "projects"):
            self.assertContains(response, f'data-filter="{value}"')

    def test_without_tile_file_the_map_has_no_tiles(self):
        with self.settings(MEDIA_ROOT="/nonexistent"):
            response = self.client.get("/map/")
        self.assertContains(response, 'data-tiles=""')

    def test_with_tile_file_its_url_is_passed(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as media:
            Path(media, "maps").mkdir()
            Path(media, "maps", "rooterium.pmtiles").write_bytes(b"x")
            with self.settings(MEDIA_ROOT=media):
                response = self.client.get("/map/")
            self.assertContains(response, 'data-terrain=""')
            Path(media, "maps", "terrain.pmtiles").write_bytes(b"x")
            with self.settings(MEDIA_ROOT=media):
                with_terrain = self.client.get("/map/")
        self.assertContains(response, 'data-tiles="/media/maps/rooterium.pmtiles"')
        self.assertContains(with_terrain, 'data-terrain="/media/maps/terrain.pmtiles"')


class TempleEntranceTests(TestCase):
    """The home page as the temple entrance (ADR 0017, brief section 6)."""

    def setUp(self):
        from core.sections import ensure_sections

        self.sections = ensure_sections()
        self.home = HomePage.objects.get()

    def get(self):
        return self.client.get("/")

    def test_portal_has_the_title_and_enter_links_to_the_chapel(self):
        response = self.get()
        self.assertContains(
            response,
            '<h1 id="portal-title" class="portal-title">Rooterium</h1>',
            html=True,
        )
        self.assertContains(
            response, '<a class="portal-enter" href="#chapel" data-enter>'
        )
        self.assertContains(response, 'id="chapel"')
        self.assertContains(response, "core/js/journey.js")

    def test_no_site_header_on_the_portal(self):
        self.assertNotContains(self.get(), 'class="site-header"')

    def test_chapel_lists_all_six_sections_with_root_symbols(self):
        content = self.get().content.decode()
        chapel = content.split('class="chapel-list"')[1].split("</ul>")[0]
        positions = [
            chapel.index(f'href="{page.url}"') for page in self.sections.values()
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            '<span class="chapel-symbol">figure with a hidden face</span>', chapel
        )

    def test_tagline_and_heading_come_from_the_admin(self):
        self.assertContains(self.get(), "Choose a path")
        self.home.tagline = "One line by the editor"
        self.home.chapel_heading = "Pick a hall"
        self.home.save_revision().publish()
        response = self.get()
        self.assertContains(response, "One line by the editor")
        self.assertContains(response, "Pick a hall")

    def test_without_assets_the_page_falls_back_to_text(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<video")
        self.assertNotContains(response, "data-portal-poster")
        self.assertNotContains(response, "data-pause")

    def test_with_assets_videos_are_added_but_hidden_until_scripted(self):
        from wagtail.documents import get_document_model

        from images.testing import make_image

        Document = get_document_model()
        loop = Document.objects.create(title="loop", file="documents/loop.mp4")
        entrance = Document.objects.create(title="entrance", file="documents/in.mp4")
        self.home.portal_poster = make_image()
        self.home.chapel_image = make_image()
        self.home.portal_video = loop
        self.home.entrance_video = entrance
        self.home.save_revision().publish()
        response = self.get()
        self.assertContains(response, 'rel="preload" as="image"')
        self.assertContains(response, "data-portal-poster")
        self.assertContains(response, f'<source src="{loop.url}" type="video/mp4">')
        self.assertContains(response, f'<source src="{entrance.url}" type="video/mp4">')
        # Videos never autoplay from the markup (reduced motion, no JS).
        self.assertNotContains(response, "autoplay")
        self.assertContains(response, "hidden data-portal-video")
        self.assertContains(response, 'class="entrance" hidden data-entrance')
        self.assertContains(response, "data-pause")
        self.assertContains(response, "data-skip")

    def test_old_home_sections_are_gone(self):
        response = self.get()
        self.assertNotContains(response, "data-map")
        self.assertNotContains(response, "Latest stories")
        self.assertNotContains(response, "signup-form")


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
