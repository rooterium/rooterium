import re
import time
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core import mail, signing
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core import spam
from newsletter.forms import CONSENT_TEXT
from newsletter.models import UNCONFIRMED_DAYS, NewsletterSubscriber


def started(seconds_ago=10):
    return signing.dumps(time.time() - seconds_ago, salt=spam._SALT)


def signup_data(**kwargs):
    return {
        "email": "reader@example.org",
        "consent": "on",
        "website": "",
        "started": started(),
    } | kwargs


def make_subscriber(email="reader@example.org", **kwargs):
    return NewsletterSubscriber.objects.create(email=email, consent_text="x", **kwargs)


class NewsletterSubscriberTests(TestCase):
    def test_new_subscriber_gets_a_random_token_and_is_unconfirmed(self):
        a = make_subscriber("a@example.org")
        b = make_subscriber("b@example.org")
        self.assertGreaterEqual(len(a.token), 40)
        self.assertNotEqual(a.token, b.token)
        self.assertFalse(a.is_confirmed)

    def test_stale_means_unconfirmed_and_older_than_the_period(self):
        old = timezone.now() - timedelta(days=UNCONFIRMED_DAYS + 1)
        stale = make_subscriber("stale@example.org", consented_at=old)
        make_subscriber("fresh@example.org")
        make_subscriber(
            "old-but-confirmed@example.org", consented_at=old, confirmed_at=old
        )
        self.assertQuerySetEqual(NewsletterSubscriber.objects.stale(), [stale])


class SignupTests(TestCase):
    def setUp(self):
        cache.clear()

    def confirm_url(self, message):
        return re.search(r"https?://[^/]+(/newsletter/confirm/[^/\s]+/)", message.body)[
            1
        ]

    def test_signup_page(self):
        response = self.client.get("/newsletter/")
        self.assertContains(
            response, "<title>Newsletter – Rooterium</title>", html=True
        )
        self.assertContains(response, str(CONSENT_TEXT))

    def test_signup_stores_consent_and_sends_confirmation_link(self):
        response = self.client.post(
            "/newsletter/", signup_data(email="Reader@Example.org")
        )
        self.assertRedirects(response, "/newsletter/check-your-inbox/")
        subscriber = NewsletterSubscriber.objects.get()
        self.assertEqual(subscriber.email, "reader@example.org")
        self.assertEqual(subscriber.consent_text, str(CONSENT_TEXT))
        self.assertIsNotNone(subscriber.consented_at)
        self.assertFalse(subscriber.is_confirmed)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["reader@example.org"])
        self.assertEqual(
            self.confirm_url(mail.outbox[0]),
            f"/newsletter/confirm/{subscriber.token}/",
        )

    def test_consent_is_required(self):
        response = self.client.post("/newsletter/", signup_data(consent=""))
        self.assertContains(response, "Error:")
        self.assertContains(
            response, "Please confirm that you want to receive the newsletter."
        )
        self.assertFalse(NewsletterSubscriber.objects.exists())

    def test_invalid_email(self):
        response = self.client.post("/newsletter/", signup_data(email="not-an-email"))
        self.assertContains(response, 'aria-invalid="true"')
        self.assertFalse(NewsletterSubscriber.objects.exists())

    def test_signing_up_again_before_confirming_resends_the_link(self):
        self.client.post("/newsletter/", signup_data())
        self.client.post("/newsletter/", signup_data())
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_confirmed_address_gets_the_same_answer_but_no_email(self):
        make_subscriber(confirmed_at=timezone.now())
        response = self.client.post("/newsletter/", signup_data())
        self.assertRedirects(response, "/newsletter/check-your-inbox/")
        self.assertEqual(mail.outbox, [])

    def test_honeypot_saves_nothing(self):
        response = self.client.post("/newsletter/", signup_data(website="x"))
        self.assertRedirects(response, "/newsletter/check-your-inbox/")
        self.assertFalse(NewsletterSubscriber.objects.exists())
        self.assertEqual(mail.outbox, [])

    def test_too_fast_is_refused(self):
        response = self.client.post("/newsletter/", signup_data(started=started(1)))
        self.assertContains(response, "Please check your entries")
        self.assertFalse(NewsletterSubscriber.objects.exists())

    def test_rate_limit(self):
        for number in range(spam.RATE_LIMIT):
            self.client.post(
                "/newsletter/", signup_data(email=f"r{number}@example.org")
            )
        response = self.client.post("/newsletter/", signup_data())
        self.assertEqual(response.status_code, 429)
        self.assertEqual(NewsletterSubscriber.objects.count(), spam.RATE_LIMIT)

    def test_signup_deletes_stale_signups(self):
        old = timezone.now() - timedelta(days=UNCONFIRMED_DAYS + 1)
        make_subscriber("stale@example.org", consented_at=old)
        self.client.post("/newsletter/", signup_data())
        self.assertQuerySetEqual(
            NewsletterSubscriber.objects.values_list("email", flat=True),
            ["reader@example.org"],
        )

    def test_failing_mail_server_is_logged(self):
        with (
            mock.patch("newsletter.signup.send_mail", side_effect=OSError),
            self.assertLogs("newsletter.signup", "ERROR"),
        ):
            response = self.client.post("/newsletter/", signup_data())
        self.assertRedirects(response, "/newsletter/check-your-inbox/")

    def test_home_page_has_the_signup_form(self):
        response = self.client.get("/")
        self.assertContains(response, 'action="/newsletter/"')
        self.assertContains(response, 'name="started"')

    def test_footer_links_to_the_newsletter(self):
        self.assertContains(self.client.get("/stories/"), 'href="/newsletter/"')


class ConfirmTests(TestCase):
    def test_get_does_not_confirm(self):
        # Mail programs open links by themselves.
        subscriber = make_subscriber()
        response = self.client.get(f"/newsletter/confirm/{subscriber.token}/")
        self.assertContains(response, "Yes, subscribe me")
        subscriber.refresh_from_db()
        self.assertFalse(subscriber.is_confirmed)

    def test_post_confirms(self):
        subscriber = make_subscriber()
        response = self.client.post(f"/newsletter/confirm/{subscriber.token}/")
        self.assertContains(response, "You are subscribed")
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_confirmed)

    def test_confirming_twice_keeps_the_first_timestamp(self):
        first = timezone.now() - timedelta(days=30)
        subscriber = make_subscriber(confirmed_at=first)
        self.client.post(f"/newsletter/confirm/{subscriber.token}/")
        subscriber.refresh_from_db()
        self.assertEqual(subscriber.confirmed_at, first)

    def test_expired_or_unknown_link(self):
        old = timezone.now() - timedelta(days=UNCONFIRMED_DAYS + 1)
        subscriber = make_subscriber(consented_at=old)
        for token in [subscriber.token, "unknown"]:
            with self.subTest(token=token):
                response = self.client.post(f"/newsletter/confirm/{token}/")
                self.assertContains(
                    response, "This link is no longer valid", status_code=404
                )
        subscriber.refresh_from_db()
        self.assertFalse(subscriber.is_confirmed)


class UnsubscribeTests(TestCase):
    def test_get_asks_first(self):
        subscriber = make_subscriber(confirmed_at=timezone.now())
        response = self.client.get(f"/newsletter/unsubscribe/{subscriber.token}/")
        self.assertContains(response, "Yes, unsubscribe me")
        self.assertTrue(NewsletterSubscriber.objects.exists())

    def test_post_deletes_the_address(self):
        subscriber = make_subscriber(confirmed_at=timezone.now())
        response = self.client.post(f"/newsletter/unsubscribe/{subscriber.token}/")
        self.assertContains(response, "You are unsubscribed")
        self.assertFalse(NewsletterSubscriber.objects.exists())

    def test_unknown_link(self):
        response = self.client.get("/newsletter/unsubscribe/unknown/")
        self.assertContains(response, "not (or no longer) subscribed", status_code=404)


class PruneCommandTests(TestCase):
    def test_deletes_stale_signups(self):
        old = timezone.now() - timedelta(days=UNCONFIRMED_DAYS + 1)
        make_subscriber("stale@example.org", consented_at=old)
        make_subscriber("fresh@example.org")
        out = StringIO()
        call_command("prune_newsletter_signups", stdout=out)
        self.assertIn("Deleted 1", out.getvalue())
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
