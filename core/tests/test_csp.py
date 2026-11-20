from django.contrib.auth import get_user_model
from django.test import TestCase


class ContentSecurityPolicyTests(TestCase):
    def test_public_pages_get_a_strict_policy(self):
        policy = self.client.get("/")["Content-Security-Policy"]
        self.assertIn("default-src 'self'", policy)
        self.assertIn("script-src 'self'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertNotIn("unsafe-inline", policy)

    def test_only_youtube_nocookie_may_be_framed(self):
        policy = self.client.get("/")["Content-Security-Policy"]
        self.assertIn("frame-src https://www.youtube-nocookie.com", policy)

    def test_404_pages_get_the_policy(self):
        response = self.client.get("/does-not-exist/")
        self.assertIn("Content-Security-Policy", response)

    def test_admin_is_excluded(self):
        self.assertNotIn("Content-Security-Policy", self.client.get("/admin/login/"))
        self.assertNotIn(
            "Content-Security-Policy", self.client.get("/django-admin/login/")
        )

    def test_public_templates_have_no_inline_styles_or_scripts(self):
        user = get_user_model().objects.create_user("u", "u@example.org", "pw")
        self.client.force_login(user)
        html = self.client.get("/").content.decode()
        self.assertNotIn(" style=", html)
        self.assertNotIn("<style", html)
        self.assertNotRegex(html, r"<script(?![^>]*\b(src|type=\"application/json\"))")
