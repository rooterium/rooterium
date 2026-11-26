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
from stories.models import CategoryPage, StoryPage, ThemeIndexPage


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
        self.religion = ThemeIndexPage(title="Religion", theme=Theme.RELIGION)
        self.home.add_child(instance=self.religion)

    def test_reading_time_is_at_least_one_minute(self):
        story = make_story(self.religion)
        self.assertEqual(story.reading_time, 1)
        long = make_story(
            self.religion,
            title="Long",
            body=[("paragraph", "<p>" + "word " * 1000 + "</p>")],
        )
        self.assertEqual(long.reading_time, 5)

    def test_related_place_links_to_the_map(self):
        story = make_story(self.religion)
        place = make_place()
        story.related_places.add(place)
        story.save_revision().publish()
        response = self.client.get(story.url)
        self.assertContains(response, "Places in this story")
        self.assertContains(response, f'href="/?place=place-{place.pk}#explore"')

    def test_draft_places_are_not_listed(self):
        story = make_story(self.religion)
        story.related_places.add(make_place(name="[Draft]", live=False))
        story.save_revision().publish()
        self.assertNotContains(self.client.get(story.url), "Places in this story")

    def test_more_stories_of_the_same_theme(self):
        story = make_story(self.religion, title="One")
        other = make_story(self.religion, title="Two")
        symbols = ThemeIndexPage(title="Symbols", theme=Theme.SYMBOLS)
        self.home.add_child(instance=symbols)
        make_story(symbols, title="Elsewhere")
        self.assertEqual(list(story.more_stories()), [other.page_ptr.specific])
        response = self.client.get(story.url)
        self.assertContains(response, "More on Religion")

    def test_story_uses_its_hero_image_for_open_graph(self):
        story = make_story(self.religion)
        response = self.client.get(story.url)
        self.assertContains(response, ".fill-1200x630.")

    def test_youtube_is_not_loaded_before_a_click(self):
        story = make_story(
            self.religion,
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
            "/admin/newsletter-subscribers/",
            f"/admin/pages/add/stories/themeindexpage/{home.pk}/",
            f"/admin/pages/add/stories/storypage/{theme.pk}/",
            f"/admin/pages/add/pages/simplepage/{home.pk}/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_root_page_exists(self):
        self.assertTrue(Page.objects.filter(depth=1).exists())


class StoryOverviewTests(TestCase):
    def setUp(self):
        home = HomePage.objects.get()
        self.religion = ThemeIndexPage(title="Religion", theme=Theme.RELIGION)
        self.music = ThemeIndexPage(title="Music", theme=Theme.MUSIC)
        home.add_child(instance=self.religion)
        home.add_child(instance=self.music)
        self.spear = make_story(self.religion, title="The monastery of the spear")
        self.duduk = make_story(self.music, title="The duduk")

    def test_lists_all_live_stories_with_title_and_description(self):
        draft = make_story(self.religion, title="[Draft story]")
        draft.unpublish()
        response = self.client.get("/stories/")
        self.assertContains(response, "<title>Stories – Rooterium</title>", html=True)
        self.assertContains(response, "The monastery of the spear")
        self.assertContains(response, "The duduk")
        self.assertNotContains(response, "[Draft story]")

    def test_theme_links_go_to_the_theme_pages(self):
        response = self.client.get("/stories/")
        self.assertContains(response, f'href="{self.religion.url}"')
        self.assertContains(response, f'href="{self.music.url}"')
        self.assertContains(
            response,
            '<a class="chip" href="/stories/" aria-current="page">All</a>',
            html=True,
        )

    def test_paginates_after_twelve(self):
        for number in range(12):
            make_story(self.music, title=f"[Story {number}]")
        response = self.client.get("/stories/")
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, 'rel="next"')
        self.assertEqual(self.client.get("/stories/?page=2").status_code, 200)

    def test_main_navigation_links_to_stories(self):
        response = self.client.get("/stories/")
        self.assertContains(
            response, '<a href="/stories/" aria-current="page">Stories</a>', html=True
        )
        self.assertContains(
            self.client.get("/"), '<a href="/stories/">Stories</a>', html=True
        )

    def test_theme_page_shows_its_stories_and_theme_links(self):
        response = self.client.get(self.religion.url)
        self.assertContains(response, "The monastery of the spear")
        self.assertNotContains(response, "The duduk")
        self.assertContains(
            response,
            f'<a class="chip" href="{self.religion.url}" aria-current="page">Religion</a>',
            html=True,
        )


class SectionHierarchyTests(TestCase):
    """Sections, categories and the section lookup (ADR 0018)."""

    def setUp(self):
        self.home = HomePage.objects.get()
        self.symbols = ThemeIndexPage(title="Symbols", theme=Theme.SYMBOLS)
        self.home.add_child(instance=self.symbols)
        self.category = CategoryPage(title="Tree of life", intro="Its roots.")
        self.symbols.add_child(instance=self.category)

    def test_six_sections_in_chapel_order(self):
        self.assertEqual(
            Theme.values,
            ["music", "symbols", "history", "artifacts", "people", "religion"],
        )
        self.assertEqual(Theme.PEOPLE.label, "Key people")

    def test_section_of_a_story_in_a_category_is_the_nearest_section(self):
        story = make_story(self.category)
        self.assertEqual(story.theme, "symbols")
        self.assertEqual(story.get_theme_display(), "Symbols")
        self.assertEqual(story.theme_page.pk, self.symbols.pk)
        self.assertEqual(story.category.pk, self.category.pk)

    def test_story_directly_in_a_section_has_no_category(self):
        story = make_story(self.symbols)
        self.assertEqual(story.theme, "symbols")
        self.assertIsNone(story.category)

    def test_allowed_parents_and_children(self):
        self.assertEqual(
            set(ThemeIndexPage.allowed_subpage_models()), {CategoryPage, StoryPage}
        )
        self.assertEqual(
            set(CategoryPage.allowed_parent_page_models()), {ThemeIndexPage}
        )
        self.assertEqual(set(CategoryPage.allowed_subpage_models()), {StoryPage})
        self.assertEqual(
            set(StoryPage.allowed_parent_page_models()), {ThemeIndexPage, CategoryPage}
        )

    def test_more_stories_come_from_the_whole_section(self):
        in_category = make_story(self.category, title="In the category")
        direct = make_story(self.symbols, title="Directly in the section")
        music = ThemeIndexPage(title="Music", theme=Theme.MUSIC)
        self.home.add_child(instance=music)
        make_story(music, title="Other section")
        self.assertEqual(list(in_category.more_stories()), [direct])

    def test_section_page_lists_categories_and_direct_stories(self):
        make_story(self.category, title="In the category")
        make_story(self.symbols, title="Directly in the section")
        response = self.client.get(self.symbols.url)
        self.assertContains(response, "Tree of life")
        self.assertContains(response, "Directly in the section")
        self.assertNotContains(response, "In the category")

    def test_category_page_lists_its_stories(self):
        make_story(self.category, title="In the category")
        response = self.client.get(self.category.url)
        self.assertContains(response, "<h1>Tree of life</h1>", html=True)
        self.assertContains(response, "In the category")
        self.assertContains(response, f'href="{self.symbols.url}"')

    def test_legacy_value_does_not_break_the_label(self):
        legacy = ThemeIndexPage(title="Myths", theme=Theme.RELIGION)
        self.home.add_child(instance=legacy)
        ThemeIndexPage.objects.filter(pk=legacy.pk).update(theme="myths")
        story = make_story(legacy)
        self.assertEqual(story.get_theme_display(), "Religion")
        self.assertEqual(self.client.get(story.url).status_code, 200)
