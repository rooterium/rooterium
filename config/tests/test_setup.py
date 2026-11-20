"""Smoke tests for the project setup."""

from django.conf import settings
from django.test import TestCase


class SettingsTests(TestCase):
    def test_locale_and_timezone(self):
        self.assertEqual(settings.LANGUAGE_CODE, "en")
        self.assertEqual(settings.TIME_ZONE, "Europe/Vienna")
        self.assertTrue(settings.USE_TZ)

    def test_uses_postgresql(self):
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )


class AdminTests(TestCase):
    def test_wagtail_admin_login_page_is_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "wagtail")

    def test_django_admin_login_page_is_reachable_and_english(self):
        response = self.client.get("/django-admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{settings.SITE_SHORT_NAME} administration")
        self.assertContains(response, 'lang="en"')
