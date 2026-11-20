"""Smoke tests for the project setup."""

from django.conf import settings
from django.test import TestCase


class SettingsTests(TestCase):
    def test_locale_and_timezone(self):
        self.assertEqual(settings.LANGUAGE_CODE, "de-ch")
        self.assertEqual(settings.TIME_ZONE, "Europe/Zurich")
        self.assertTrue(settings.USE_TZ)

    def test_uses_postgresql(self):
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )


class AdminTests(TestCase):
    def test_admin_login_page_is_reachable_and_german(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{settings.SITE_SHORT_NAME} – Verwaltung")
        self.assertContains(response, 'lang="de-ch"')
