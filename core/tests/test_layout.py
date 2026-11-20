"""Tests for the base layout and SEO tags."""

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.views.generic import TemplateView

from core.seo import SeoMixin, build_title


@override_settings(SITE_TITLE="Short – Long Name", SITE_SHORT_NAME="Short")
class BuildTitleTests(SimpleTestCase):
    def test_without_page_title_uses_site_title(self):
        self.assertEqual(build_title(), "Short – Long Name")

    def test_with_page_title_appends_short_name(self):
        self.assertEqual(build_title("Events"), "Events – Short")


class SeoMixinTests(SimpleTestCase):
    def test_puts_title_and_description_into_context(self):
        class View(SeoMixin, TemplateView):
            template_name = "base.html"
            page_title = "Events"
            meta_description = "Upcoming events"

        view = View()
        view.setup(RequestFactory().get("/"))
        context = view.get_context_data()

        self.assertEqual(context["page_title"], "Events")
        self.assertEqual(context["meta_description"], "Upcoming events")


class HomePageTests(TestCase):
    def setUp(self):
        self.response = self.client.get("/")

    def test_renders(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "home/home_page.html")

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

    def test_language_is_english(self):
        self.assertContains(self.response, '<html lang="en">')

    def test_brand_links_home_and_marks_current_page(self):
        self.assertContains(
            self.response,
            '<a class="brand" href="/" aria-current="page">',
        )


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_404_page_is_english(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(
            response,
            f"<title>Page not found – {settings.SITE_SHORT_NAME}</title>",
            status_code=404,
        )


class WebAssetTests(TestCase):
    def test_default_open_graph_image_is_absolute(self):
        response = self.client.get("/")
        self.assertContains(
            response,
            '<meta property="og:image" '
            'content="http://testserver/static/core/img/og-default.jpg">',
            html=True,
        )

    def test_icons_are_linked(self):
        response = self.client.get("/")
        self.assertContains(response, "core/img/favicon-32.png")
        self.assertContains(response, "core/img/apple-touch-icon.png")

    def test_favicon_ico_redirects_to_static_file(self):
        response = self.client.get("/favicon.ico")
        self.assertRedirects(
            response,
            "/static/core/img/favicon.ico",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_generated_files_exist(self):
        from pathlib import Path

        img = Path(settings.BASE_DIR) / "core/static/core/img"
        for name in (
            "favicon.ico",
            "favicon-32.png",
            "apple-touch-icon.png",
            "icon-512.png",
            "og-default.jpg",
        ):
            with self.subTest(name=name):
                self.assertTrue((img / name).is_file())


class HeaderFooterTests(TestCase):
    """Header and footer follow the variant B mockup (design/)."""

    def test_header_has_map_link_and_subscribe_button(self):
        response = self.client.get("/stories/")
        self.assertContains(response, '<a href="/#explore">Map</a>', html=True)
        self.assertContains(
            response,
            '<a class="button nav-subscribe" href="/newsletter/">Subscribe</a>',
            html=True,
        )

    def test_about_link_only_when_the_page_is_live(self):
        from home.models import HomePage
        from pages.models import Purpose, SimplePage

        self.assertNotContains(self.client.get("/stories/"), ">About</a>")
        about = SimplePage(title="About", purpose=Purpose.ABOUT, body="<p>x</p>")
        HomePage.objects.get().add_child(instance=about)
        self.assertContains(
            self.client.get("/stories/"), f'<a href="{about.url}">About</a>', html=True
        )

    def test_footer_names_the_project_owner(self):
        response = self.client.get("/stories/")
        self.assertContains(
            response, f"Rooterium is a personal project by {settings.SITE_OWNER}."
        )

    def test_armenian_name_only_when_set(self):
        self.assertNotContains(self.client.get("/stories/"), "brand-native")
        with override_settings(SITE_NATIVE_NAME="[hy]"):
            self.assertContains(
                self.client.get("/stories/"),
                '<span class="brand-native" lang="hy">[hy]</span>',
            )
