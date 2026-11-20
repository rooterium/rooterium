import time
from unittest import mock

from django.core import mail, signing
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from events.models import Event
from projects.models import Project, ProjectKind
from submissions import spam

EDITOR = "editor@example.org"


def started(seconds_ago=10):
    """A form timestamp from `seconds_ago` seconds ago."""
    return signing.dumps(time.time() - seconds_ago, salt=spam._SALT)


def event_data(**kwargs):
    return {
        "title": "[Suggested concert]",
        "start_date": "2099-05-01",
        "end_date": "",
        "city": "[City]",
        "country": "[Country]",
        "link": "https://example.org/concert",
        "submitted_by_email": "submitter@example.org",
        "website": "",
        "started": started(),
    } | kwargs


def project_data(**kwargs):
    return {
        "name": "[Suggested ensemble]",
        "kind": ProjectKind.MUSIC,
        "city": "[City]",
        "country": "[Country]",
        "link": "https://example.org/ensemble",
        "short_description": "[Short description]",
        "submitted_by_email": "submitter@example.org",
        "website": "",
        "started": started(),
    } | kwargs


@override_settings(EDITOR_NOTIFICATION_EMAIL=EDITOR)
class EventSubmissionTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_form_page(self):
        response = self.client.get("/suggest/event/")
        self.assertContains(
            response, "<title>Suggest an event – Rooterium</title>", html=True
        )
        self.assertContains(response, 'name="started"')
        self.assertContains(response, 'class="form-trap" aria-hidden="true"')

    def test_creates_a_draft_and_notifies_the_editor(self):
        response = self.client.post("/suggest/event/", event_data())
        self.assertRedirects(response, "/suggest/thanks/")
        event = Event.objects.get()
        self.assertFalse(event.live)
        self.assertEqual(event.submitted_by_email, "submitter@example.org")
        self.assertIsNotNone(event.latest_revision)
        self.assertFalse(Event.objects.upcoming().exists())

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [EDITOR])
        self.assertIn("[Suggested concert]", message.subject)
        self.assertIn(f"/admin/snippets/events/event/edit/{event.pk}/", message.body)
        self.assertIn("Link: https://example.org/concert", message.body)

    def test_editor_can_publish_the_draft(self):
        self.client.post("/suggest/event/", event_data())
        event = Event.objects.get()
        event.latest_revision.publish()
        event.refresh_from_db()
        self.assertTrue(event.live)
        self.assertQuerySetEqual(Event.objects.upcoming(), [event])

    def test_submitter_email_is_not_shown_publicly(self):
        self.client.post("/suggest/event/", event_data())
        Event.objects.get().latest_revision.publish()
        response = self.client.get("/events/")
        self.assertContains(response, "[Suggested concert]")
        self.assertNotContains(response, "submitter@example.org")

    def test_validation_errors_are_shown_with_text(self):
        response = self.client.post(
            "/suggest/event/",
            event_data(start_date="2099-05-02", end_date="2099-05-01", link=""),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Error:")
        self.assertContains(response, "The end date cannot be before the start date.")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertFalse(Event.objects.exists())

    def test_email_is_required(self):
        response = self.client.post(
            "/suggest/event/", event_data(submitted_by_email="")
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.exists())

    def test_honeypot_pretends_success_but_saves_nothing(self):
        response = self.client.post(
            "/suggest/event/", event_data(website="https://spam.example")
        )
        self.assertRedirects(response, "/suggest/thanks/")
        self.assertFalse(Event.objects.exists())
        self.assertEqual(mail.outbox, [])

    def test_too_fast_is_refused(self):
        response = self.client.post("/suggest/event/", event_data(started=started(1)))
        self.assertContains(
            response, "Please check your entries and send the form again."
        )
        self.assertFalse(Event.objects.exists())

    def test_missing_forged_or_stale_timestamp_is_refused(self):
        for token in ["", "forged", started(2 * 24 * 60 * 60)]:
            with self.subTest(token=token):
                response = self.client.post(
                    "/suggest/event/", event_data(started=token)
                )
                self.assertContains(
                    response, "Please check your entries and send the form again."
                )
        self.assertFalse(Event.objects.exists())

    def test_rate_limit_per_client(self):
        for number in range(spam.RATE_LIMIT):
            self.client.post("/suggest/event/", event_data(title=f"[Event {number}]"))
        response = self.client.post("/suggest/event/", event_data())
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Please try again in an hour.", status_code=429)
        self.assertEqual(Event.objects.count(), spam.RATE_LIMIT)
        # Another client is not affected.
        other = self.client.post(
            "/suggest/event/", event_data(), HTTP_X_FORWARDED_FOR="203.0.113.9"
        )
        self.assertRedirects(other, "/suggest/thanks/")

    @override_settings(EDITOR_NOTIFICATION_EMAIL="")
    def test_without_editor_address_the_draft_is_saved_without_email(self):
        self.client.post("/suggest/event/", event_data())
        self.assertTrue(Event.objects.exists())
        self.assertEqual(mail.outbox, [])

    def test_failing_mail_server_does_not_lose_the_submission(self):
        with (
            mock.patch("submissions.notify.send_mail", side_effect=OSError),
            self.assertLogs("submissions.notify", "ERROR"),
        ):
            response = self.client.post("/suggest/event/", event_data())
        self.assertRedirects(response, "/suggest/thanks/")
        self.assertTrue(Event.objects.exists())

    def test_events_page_links_to_the_form(self):
        self.assertContains(self.client.get("/events/"), 'href="/suggest/event/"')


@override_settings(EDITOR_NOTIFICATION_EMAIL=EDITOR)
class ProjectSubmissionTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_creates_a_draft_and_notifies_the_editor(self):
        response = self.client.post("/suggest/project/", project_data())
        self.assertRedirects(response, "/suggest/thanks/")
        project = Project.objects.get()
        self.assertFalse(project.live)
        self.assertFalse(Project.objects.public().exists())
        self.assertIn("Type: Music", mail.outbox[0].body)

    def test_short_description_is_limited(self):
        response = self.client.post(
            "/suggest/project/", project_data(short_description="x" * 301)
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.exists())

    def test_projects_page_links_to_the_form(self):
        self.assertContains(self.client.get("/projects/"), 'href="/suggest/project/"')


class ThanksPageTests(TestCase):
    def test_thanks_page(self):
        response = self.client.get("/suggest/thanks/")
        self.assertContains(response, "<title>Thank you – Rooterium</title>", html=True)


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
        with mock.patch("submissions.spam.time.time", return_value=time.time() + 5):
            self.assertFalse(spam.filled_in_too_fast(token))
