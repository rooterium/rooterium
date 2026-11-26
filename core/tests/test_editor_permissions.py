"""The editor group can do its work in the Wagtail admin (ADR 0014)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from core.themes import Theme
from home.models import HomePage
from stories.models import ThemeIndexPage


class EditorPermissionTests(TestCase):
    def setUp(self):
        self.editor = get_user_model().objects.create_user(
            "editor", "editor@example.org", "pw"
        )
        self.editor.groups.add(Group.objects.get(name="Editors"))
        self.client.force_login(self.editor)

    def test_editor_is_not_a_superuser(self):
        self.assertFalse(self.editor.is_superuser)

    def test_snippet_permissions(self):
        for model in ("places.place", "events.event", "projects.project"):
            app, name = model.split(".")
            for action in ("add", "change", "delete", "publish", "view"):
                with self.subTest(perm=f"{app}.{action}_{name}"):
                    self.assertTrue(self.editor.has_perm(f"{app}.{action}_{name}"))

    def test_newsletter_is_view_only(self):
        self.assertTrue(self.editor.has_perm("newsletter.view_newslettersubscriber"))
        self.assertFalse(self.editor.has_perm("newsletter.change_newslettersubscriber"))
        self.assertEqual(
            self.client.get("/admin/newsletter-subscribers/").status_code, 200
        )

    def test_editor_can_publish_pages(self):
        home = HomePage.objects.get()
        theme = ThemeIndexPage(title="Religion", theme=Theme.RELIGION)
        home.add_child(instance=theme)
        perms = theme.permissions_for_user(self.editor)
        self.assertTrue(perms.can_add_subpage())
        self.assertTrue(perms.can_publish())

    def test_admin_views_load(self):
        for url in [
            "/admin/",
            "/admin/snippets/places/place/add/",
            "/admin/snippets/events/event/",
            "/admin/snippets/projects/project/",
            "/admin/images/",
            "/admin/images/multiple/add/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
