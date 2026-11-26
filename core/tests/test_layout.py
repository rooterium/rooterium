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

    def test_brand_links_to_the_chapel(self):
        # Every page but the portal has the header.
        self.assertContains(
            self.client.get("/stories/"), '<a class="brand" href="/#chapel">'
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
    """Temple frame (ADR 0017, temple brief section 6)."""

    def setUp(self):
        from core.sections import ensure_sections

        self.sections = ensure_sections()

    def test_header_has_only_the_name_and_the_sections_menu(self):
        response = self.client.get("/stories/")
        header = response.content.decode().split('<header class="site-header">')[1]
        header = header.split("</header>")[0]
        self.assertIn('<summary class="sections-toggle">Sections</summary>', header)
        self.assertNotIn("Subscribe", header)
        self.assertNotIn("/map/", header)

    def test_sections_menu_lists_the_six_sections_in_order(self):
        content = self.client.get("/stories/").content.decode()
        menu = content.split('class="sections-panel"')[1].split("</nav>")[0]
        positions = [
            menu.index(f'href="{page.url}"') for page in self.sections.values()
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('<span class="sections-symbol">duduk</span>', menu)

    def test_current_section_is_marked(self):
        music = self.sections["music"]
        self.assertContains(
            self.client.get(music.url), f'<a href="{music.url}" aria-current="page">'
        )

    def test_footer_links_around_the_temple(self):
        response = self.client.get("/stories/")
        self.assertContains(response, "Around the temple")
        for href, label in [
            ("/map/", "Map"),
            ("/events/", "Events"),
            ("/projects/", "Projects"),
            ("/newsletter/", "Newsletter"),
        ]:
            with self.subTest(label=label):
                self.assertContains(
                    response, f'<a href="{href}">{label}</a>', html=True
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
