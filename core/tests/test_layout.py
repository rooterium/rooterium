"""Tests for the base layout and SEO tags."""

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.views.generic import TemplateView

from core.seo import SeoMixin, build_title


@override_settings(SITE_TITLE="Kurz – Langer Name", SITE_SHORT_NAME="Kurz")
class BuildTitleTests(SimpleTestCase):
    def test_without_page_title_uses_site_title(self):
        self.assertEqual(build_title(), "Kurz – Langer Name")

    def test_with_page_title_appends_short_name(self):
        self.assertEqual(build_title("Kontakt"), "Kontakt – Kurz")


class SeoMixinTests(SimpleTestCase):
    def test_puts_title_and_description_into_context(self):
        class View(SeoMixin, TemplateView):
            template_name = "base.html"
            page_title = "Kontakt"
            meta_description = "So erreichen Sie uns"

        view = View()
        view.setup(RequestFactory().get("/"))
        context = view.get_context_data()

        self.assertEqual(context["page_title"], "Kontakt")
        self.assertEqual(context["meta_description"], "So erreichen Sie uns")


class HomePageTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("core:home"))

    def test_renders(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "core/home.html")

    def test_title_and_meta_description(self):
        self.assertContains(
            self.response, f"<title>{settings.SITE_TITLE}</title>", html=True
        )
        self.assertContains(
            self.response,
            f'<meta name="description" content="{settings.SITE_DESCRIPTION}">',
            html=True,
        )
        self.assertContains(self.response, 'property="og:title"')
        self.assertContains(
            self.response, '<link rel="canonical" href="http://testserver/">', html=True
        )

    def test_language_is_swiss_german(self):
        self.assertContains(self.response, '<html lang="de-ch">')

    def test_brand_links_home_and_marks_current_page(self):
        self.assertContains(
            self.response,
            f'<a class="brand" href="{reverse("core:home")}" aria-current="page">',
        )


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_404_page_is_german(self):
        response = self.client.get("/gibt-es-nicht/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Seite nicht gefunden", status_code=404)
        self.assertContains(
            response,
            f"<title>Seite nicht gefunden – {settings.SITE_SHORT_NAME}</title>",
            status_code=404,
        )
