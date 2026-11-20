import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def new_token():
    return secrets.token_urlsafe(32)


# Unconfirmed sign-ups are deleted after this period (data minimisation);
# the confirmation link stops working at the same time.
UNCONFIRMED_DAYS = 7


class SubscriberQuerySet(models.QuerySet):
    def stale(self):
        """Unconfirmed sign-ups older than `UNCONFIRMED_DAYS`."""
        cutoff = timezone.now() - timedelta(days=UNCONFIRMED_DAYS)
        return self.filter(confirmed_at__isnull=True, consented_at__lt=cutoff)

    def confirmable(self):
        """Sign-ups whose confirmation link still works."""
        cutoff = timezone.now() - timedelta(days=UNCONFIRMED_DAYS)
        return self.exclude(confirmed_at__isnull=True, consented_at__lt=cutoff)


class NewsletterSubscriber(models.Model):
    """A newsletter sign-up with double opt-in (`newsletter/views.py`)."""

    email = models.EmailField(_("email"), unique=True)
    consent_text = models.TextField(
        _("consent text"), help_text=_("The consent text shown at sign-up.")
    )
    consented_at = models.DateTimeField(_("consented at"), default=timezone.now)
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)
    token = models.CharField(
        _("token"), max_length=64, unique=True, default=new_token, editable=False
    )

    objects = SubscriberQuerySet.as_manager()

    class Meta:
        verbose_name = _("newsletter subscriber")
        verbose_name_plural = _("newsletter subscribers")
        ordering = ["-consented_at"]

    def __str__(self):
        return self.email

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None
