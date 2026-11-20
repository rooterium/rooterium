import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.models import Page

from core.themes import Theme
from home.models import HomePage
from images.testing import make_image
from places.tests import make_place
from stories.blocks import StoryBodyBlock, YouTubeBlock, youtube_id
from stories.models import StoryPage, ThemeIndexPage


class YouTubeTests(TestCase):
    def test_extracts_video_id_from_common_urls(self):
        for url in [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ]:
            with self.subTest(url=url):
                self.assertEqual(youtube_id(url), "dQw4w9WgXcQ")

    def test_rejects_other_urls(self):
        self.assertIsNone(youtube_id("https://vimeo.com/123"))
        self.assertIsNone(youtube_id("https://evil.example/?youtube.com/watch?v=x"))

    def test_block_rejects_non_youtube_link(self):
        block = YouTubeBlock()
        value = block.to_python({"url": "https://vimeo.com/123", "title": "x"})
        with self.assertRaises(StructBlockValidationError):
            block.clean(value)


def make_story(parent, **kwargs):
    defaults = {
        "title": "The eternity sign",
        "teaser": "[Teaser]",
        "hero_image": make_image(),
        "date": datetime.date(2026, 11, 1),
        "body": [("paragraph", "<p>[Placeholder text]</p>")],
    }
    story = StoryPage(**(defaults | kwargs))
    parent.add_child(instance=story)
    return story


class StoryPageTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.get()
        self.symbols = ThemeIndexPage(title="Symbols", theme=Theme.SYMBOLS)
        self.home.add_child(instance=self.symbols)

    def test_theme_comes_from_the_parent_page(self):
        story = make_story(self.symbols)
        self.assertEqual(story.theme, Theme.SYMBOLS)
        self.assertEqual(story.get_theme_display(), "Symbols")

    def test_page_tree_rules(self):
        self.assertTrue(ThemeIndexPage.can_create_at(self.home))
        self.assertTrue(StoryPage.can_create_at(self.symbols))
        self.assertFalse(StoryPage.can_create_at(self.home))

    def test_theme_is_unique(self):
        duplicate = ThemeIndexPage(title="More symbols", theme=Theme.SYMBOLS)
        with self.assertRaises(ValidationError):
            self.home.add_child(instance=duplicate)

    def test_theme_page_lists_live_stories_newest_first(self):
        old = make_story(self.symbols, title="Old", date=datetime.date(2026, 1, 1))
        new = make_story(self.symbols, title="New", date=datetime.date(2026, 2, 1))
        draft = make_story(self.symbols, title="Draft")
        draft.unpublish()
        self.assertQuerySetEqual(self.symbols.stories(), [new, old])

    def test_story_renders_with_sources_credit_and_meta_description(self):
        story = make_story(self.symbols)
        story.sources.create(title="[Book title]", note="[Author, year]")
        story.related_places.add(make_place())
        story.save_revision().publish()

        response = self.client.get(story.url)

        self.assertContains(response, "<title>The eternity sign – Rooterium</title>")
        self.assertContains(response, '<meta name="description" content="[Teaser]">')
        self.assertContains(response, "[Book title]")
        self.assertContains(response, "Photo: [Name] · CC BY-SA 4.0")
        self.assertContains(response, 'alt="A test image"')

    def test_all_body_blocks_render_without_external_requests(self):
        image = make_image()
        body = StoryBodyBlock().to_python(
            [
                {"type": "heading", "value": {"text": "Origins", "level": "h2"}},
                {"type": "quote", "value": {"text": "q", "source": "s"}},
                {"type": "image", "value": {"image": image.pk, "caption": "c"}},
                {
                    "type": "youtube",
                    "value": {"url": "https://youtu.be/dQw4w9WgXcQ", "title": "t"},
                },
                {
                    "type": "book_excerpt",
                    "value": {"text": "e", "book_title": "b", "author": "a"},
                },
            ]
        )
        html = str(body.render_as_block())
        self.assertIn("<h2>Origins</h2>", html)
        self.assertIn("<cite>b</cite>", html)
        self.assertNotIn("<iframe", html)


class StoryPageDesignTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.get()
        self.myths = ThemeIndexPage(title="Myths", theme=Theme.MYTHS)
        self.home.add_child(instance=self.myths)

    def test_reading_time_is_at_least_one_minute(self):
        story = make_story(self.myths)
        self.assertEqual(story.reading_time, 1)
        long = make_story(
            self.myths,
            title="Long",
            body=[("paragraph", "<p>" + "word " * 1000 + "</p>")],
        )
        self.assertEqual(long.reading_time, 5)

    def test_related_place_links_to_the_map(self):
        story = make_story(self.myths)
        place = make_place()
        story.related_places.add(place)
        story.save_revision().publish()
        response = self.client.get(story.url)
        self.assertContains(response, "Places in this story")
        self.assertContains(response, f'href="/?place=place-{place.pk}#explore"')

    def test_draft_places_are_not_listed(self):
        story = make_story(self.myths)
        story.related_places.add(make_place(name="[Draft]", live=False))
        story.save_revision().publish()
        self.assertNotContains(self.client.get(story.url), "Places in this story")

    def test_more_stories_of_the_same_theme(self):
        story = make_story(self.myths, title="One")
        other = make_story(self.myths, title="Two")
        symbols = ThemeIndexPage(title="Symbols", theme=Theme.SYMBOLS)
        self.home.add_child(instance=symbols)
        make_story(symbols, title="Elsewhere")
        self.assertEqual(list(story.more_stories()), [other.page_ptr.specific])
        response = self.client.get(story.url)
        self.assertContains(response, "More on Myths")

    def test_story_uses_its_hero_image_for_open_graph(self):
        story = make_story(self.myths)
        response = self.client.get(story.url)
        self.assertContains(response, ".fill-1200x630.")

    def test_youtube_is_not_loaded_before_a_click(self):
        story = make_story(
            self.myths,
            body=[
                (
                    "youtube",
                    {"url": "https://youtu.be/dQw4w9WgXcQ", "title": "[Video]"},
                )
            ],
        )
        response = self.client.get(story.url)
        self.assertContains(response, 'data-video-id="dQw4w9WgXcQ"')
        self.assertContains(response, "youtube-nocookie.com), which receives")
        self.assertNotContains(response, "<iframe")
        self.assertContains(response, "core/js/video.js")


class AdminSmokeTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.org", "pw")
        self.client.force_login(user)

    def test_listing_and_create_views_load(self):
        home = HomePage.objects.get()
        theme = ThemeIndexPage(title="Music", theme=Theme.MUSIC)
        home.add_child(instance=theme)
        for url in [
            "/admin/snippets/places/place/",
            "/admin/snippets/places/place/add/",
            "/admin/snippets/events/event/add/",
            "/admin/snippets/projects/project/add/",
            "/admin/newsletter/",
            f"/admin/pages/add/stories/themeindexpage/{home.pk}/",
            f"/admin/pages/add/stories/storypage/{theme.pk}/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_root_page_exists(self):
        self.assertTrue(Page.objects.filter(depth=1).exists())
