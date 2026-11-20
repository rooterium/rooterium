"""Tests for /version (commit of the running build)."""

from django.test import TestCase, override_settings

COMMIT = "0123456789abcdef0123456789abcdef01234567"


class VersionTests(TestCase):
    @override_settings(APP_COMMIT=COMMIT)
    def test_returns_commit_as_json(self):
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"commit": COMMIT, "short": "0123456"})
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_local_build_reports_dev(self):
        response = self.client.get("/version")
        self.assertEqual(response.json()["commit"], "dev")
