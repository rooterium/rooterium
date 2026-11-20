from django.test import TestCase
from wagtail.models import Site

from home.models import HomePage


class HomePageSetupTests(TestCase):
    def test_home_page_is_the_default_site_root(self):
        site = Site.objects.get(is_default_site=True)
        self.assertIsInstance(site.root_page.specific, HomePage)

    def test_only_one_home_page_allowed(self):
        self.assertEqual(HomePage.max_count, 1)
