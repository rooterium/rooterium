from django.test import TestCase

from newsletter.models import NewsletterSubscriber


class NewsletterSubscriberTests(TestCase):
    def test_new_subscriber_gets_a_random_token_and_is_unconfirmed(self):
        a = NewsletterSubscriber.objects.create(email="a@example.org", consent_text="x")
        b = NewsletterSubscriber.objects.create(email="b@example.org", consent_text="x")
        self.assertGreaterEqual(len(a.token), 40)
        self.assertNotEqual(a.token, b.token)
        self.assertFalse(a.is_confirmed)
