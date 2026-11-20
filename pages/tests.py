from django.core.exceptions import ValidationError
from django.test import TestCase

from home.models import HomePage
from pages.models import Purpose, SimplePage, footer_pages


def make_page(purpose, title, **kwargs):
    page = SimplePage(
        purpose=purpose,
        title=title,
        body=f"<p>[{title} text]</p>",
        **kwargs,
    )
    HomePage.objects.get().add_child(instance=page)
    return page


class SimplePageTests(TestCase):
    def test_renders_with_title_description_and_text(self):
        page = make_page(Purpose.ABOUT, "About", intro="[What Rooterium is]")
        response = self.client.get(page.url)
        self.assertContains(response, "<title>About – Rooterium</title>", html=True)
        self.assertContains(
            response, '<meta name="description" content="[What Rooterium is]">'
        )
        self.assertContains(response, "<p>[About text]</p>", html=True)

    def test_each_purpose_exists_once(self):
        make_page(Purpose.IMPRINT, "Imprint")
        with self.assertRaises(ValidationError):
            make_page(Purpose.IMPRINT, "Imprint 2")

    def test_only_under_the_home_page(self):
        self.assertTrue(SimplePage.can_create_at(HomePage.objects.get()))
        self.assertEqual(SimplePage.allowed_subpage_models(), [])

    def test_footer_lists_live_pages_in_fixed_order(self):
        privacy = make_page(Purpose.PRIVACY, "Privacy")
        about = make_page(Purpose.ABOUT, "About")
        imprint = make_page(Purpose.IMPRINT, "Imprint")
        imprint.unpublish()
        self.assertEqual(footer_pages(), [about, privacy])
        response = self.client.get("/stories/")
        self.assertContains(response, f'<a href="{about.url}">About</a>', html=True)
        self.assertContains(response, f'<a href="{privacy.url}">Privacy</a>', html=True)
        self.assertNotContains(response, "Imprint")

    def test_forms_link_to_the_privacy_page_once_it_exists(self):
        self.assertNotContains(
            self.client.get("/newsletter/"), "How we handle your data"
        )
        privacy = make_page(Purpose.PRIVACY, "Privacy")
        for url in ["/newsletter/", "/", "/suggest/event/"]:
            with self.subTest(url=url):
                self.assertContains(
                    self.client.get(url),
                    f'<a href="{privacy.url}">How we handle your data</a>',
                    html=True,
                )
