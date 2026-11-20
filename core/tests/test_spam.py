"""Tests for the shared spam checks (core/spam.py)."""

import time
from unittest import mock

from django.core.cache import cache
from django.test import RequestFactory, TestCase

from core import spam


class ClientIpTests(TestCase):
    def test_uses_the_last_forwarded_address(self):
        request = RequestFactory().get(
            "/", HTTP_X_FORWARDED_FOR="10.0.0.1, 198.51.100.7"
        )
        self.assertEqual(spam.client_ip(request), "198.51.100.7")

    def test_falls_back_to_remote_addr(self):
        request = RequestFactory().get("/", REMOTE_ADDR="192.0.2.1")
        self.assertEqual(spam.client_ip(request), "192.0.2.1")


class StartedTokenTests(TestCase):
    def test_fresh_token_is_too_fast(self):
        self.assertTrue(spam.filled_in_too_fast(spam.make_started_token()))

    def test_token_after_some_seconds_is_fine(self):
        token = spam.make_started_token()
        with mock.patch("core.spam.time.time", return_value=time.time() + 5):
            self.assertFalse(spam.filled_in_too_fast(token))


class RateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_scopes_are_counted_separately(self):
        request = RequestFactory().get("/", REMOTE_ADDR="192.0.2.1")
        for _ in range(spam.RATE_LIMIT):
            spam.count_submission(request, scope="a")
        self.assertTrue(spam.rate_limited(request, scope="a"))
        self.assertFalse(spam.rate_limited(request, scope="b"))
