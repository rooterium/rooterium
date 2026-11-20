"""Double opt-in: sign-up, confirmation email, confirmation, unsubscribe."""

import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import CONSENT_TEXT
from .models import UNCONFIRMED_DAYS, NewsletterSubscriber

logger = logging.getLogger(__name__)


def subscribe(request, email: str) -> None:
    """Record the consent and send the confirmation link.

    The visitor always sees the same answer, whether the address is new,
    waiting for confirmation or already subscribed, so the form does not
    reveal who is subscribed. Already confirmed addresses get no email.
    """
    NewsletterSubscriber.objects.stale().delete()
    subscriber = NewsletterSubscriber.objects.filter(email__iexact=email).first()
    if subscriber and subscriber.is_confirmed:
        return
    if subscriber is None:
        subscriber = NewsletterSubscriber(email=email)
    subscriber.consent_text = str(CONSENT_TEXT)
    subscriber.consented_at = timezone.now()
    subscriber.save()
    send_confirmation(request, subscriber)


def send_confirmation(request, subscriber) -> None:
    confirm_url = request.build_absolute_uri(
        reverse("newsletter:confirm", args=[subscriber.token])
    )
    body = render_to_string(
        "newsletter/email/confirm.txt",
        {"confirm_url": confirm_url, "days": UNCONFIRMED_DAYS},
    )
    try:
        send_mail(
            _("Please confirm your Rooterium newsletter sign-up"),
            body,
            None,
            [subscriber.email],
        )
    except Exception:
        # The visitor can simply sign up again; the unconfirmed entry is
        # deleted after UNCONFIRMED_DAYS.
        logger.exception("Could not send the newsletter confirmation.")
