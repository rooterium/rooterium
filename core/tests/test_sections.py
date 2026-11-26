import io

from django.core.management import call_command
from django.test import TestCase
from wagtail.contrib.redirects.models import Redirect

from core.sections import SYMBOLS_CATEGORIES
from core.themes import Theme
from home.models import HomePage
from stories.models import CategoryPage, StoryPage, ThemeIndexPage
from stories.tests import make_story


def theme_page(home, value, title):
    """A published theme page; version 1 values (no longer valid choices,
    so Wagtail's clean would refuse them) are set in the database, as they
    are on a server that still has version 1 content."""
    placeholder = {"traditions": Theme.ARTIFACTS, "myths": Theme.PEOPLE}
    page = ThemeIndexPage(
        title=title, slug=value, theme=placeholder.get(value, value), intro=""
    )
    home.add_child(instance=page)
    page.save_revision().publish()
    if value in placeholder:
        ThemeIndexPage.objects.filter(pk=page.pk).update(theme=value)
        page.refresh_from_db()
    return page


def restructure():
    call_command("restructure_sections", stdout=io.StringIO())


class RestructureSectionsTests(TestCase):
    """Version 1 theme pages become the six sections (ADR 0018)."""

    def setUp(self):
        self.home = HomePage.objects.get()
        self.pages = {}
        for value, title in [
            ("history", "History"),
            ("traditions", "Traditions"),
            ("myths", "Myths"),
            ("symbols", "Symbols"),
            ("music", "Music"),
        ]:
            self.pages[value] = theme_page(self.home, value, title)
        self.spear = make_story(self.pages["myths"], title="The monastery of the spear")
        self.spear.save_revision().publish()
        self.khachkars = make_story(self.pages["traditions"], title="Khachkars")
        self.khachkars.save_revision().publish()

    def test_myths_page_becomes_religion_with_its_stories(self):
        restructure()
        religion = ThemeIndexPage.objects.get(theme=Theme.RELIGION)
        self.assertEqual(religion.pk, self.pages["myths"].pk)
        self.assertEqual((religion.title, religion.slug), ("Religion", "religion"))
        self.spear.refresh_from_db()
        self.assertEqual(self.spear.get_parent().pk, religion.pk)
        self.assertEqual(self.spear.specific.theme, "religion")
        # The admin edits the latest revision: it must hold the new value.
        self.assertEqual(religion.get_latest_revision_as_object().theme, "religion")

    def test_traditions_stories_move_to_history_and_the_page_goes(self):
        restructure()
        self.assertFalse(ThemeIndexPage.objects.filter(theme="traditions").exists())
        self.khachkars.refresh_from_db()
        self.assertEqual(self.khachkars.get_parent().pk, self.pages["history"].pk)

    def test_old_urls_redirect(self):
        # Wagtail creates some redirects in on_commit hooks.
        with self.captureOnCommitCallbacks(execute=True):
            restructure()
        response = self.client.get("/traditions/khachkars/")
        self.assertRedirects(response, "/history/khachkars/", status_code=301)
        self.assertRedirects(
            self.client.get("/myths/the-monastery-of-the-spear/"),
            "/religion/the-monastery-of-the-spear/",
            status_code=301,
        )
        self.assertTrue(Redirect.objects.exists())

    def test_creates_the_missing_sections_and_the_symbols_categories(self):
        restructure()
        self.assertEqual(
            sorted(ThemeIndexPage.objects.values_list("theme", flat=True)),
            sorted(Theme.values),
        )
        people = ThemeIndexPage.objects.get(theme=Theme.PEOPLE)
        self.assertEqual(
            (people.title, people.slug, people.live), ("Key people", "key-people", True)
        )
        symbols = ThemeIndexPage.objects.get(theme=Theme.SYMBOLS)
        self.assertEqual(symbols.motto, "Symbols are the language of memory.")
        self.assertEqual(symbols.root_symbol, "arevakhach (eternity sign)")
        self.assertEqual(
            list(
                CategoryPage.objects.child_of(symbols).values_list("title", flat=True)
            ),
            [title for title, _, _ in SYMBOLS_CATEGORIES],
        )

    def test_running_twice_changes_nothing(self):
        restructure()
        counts = (ThemeIndexPage.objects.count(), CategoryPage.objects.count())
        restructure()
        self.assertEqual(
            (ThemeIndexPage.objects.count(), CategoryPage.objects.count()), counts
        )
        self.assertEqual(StoryPage.objects.count(), 2)

    def test_editor_text_and_drafts_are_kept(self):
        music = self.pages["music"]
        music.root_symbol = "kamancha"
        music.save_revision().publish()
        history = self.pages["history"]
        history.intro = "Draft intro by the editor"
        history.save_revision()  # unpublished draft
        restructure()
        music.refresh_from_db()
        self.assertEqual(music.root_symbol, "kamancha")
        history.refresh_from_db()
        self.assertTrue(history.has_unpublished_changes)
        draft = history.get_latest_revision_as_object()
        self.assertEqual(draft.intro, "Draft intro by the editor")
        self.assertEqual(draft.root_symbol, "Ararat, fortress")
        self.assertEqual(history.root_symbol, "")  # the draft is not published
