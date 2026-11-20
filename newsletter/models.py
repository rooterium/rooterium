import secrets

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def new_token():
    return secrets.token_urlsafe(32)


class NewsletterSubscriber(models.Model):
    """A newsletter sign-up. The double opt-in flow follows in milestone 7."""

    email = models.EmailField(_("email"), unique=True)
    consent_text = models.TextField(
        _("consent text"), help_text=_("The consent text shown at sign-up.")
    )
    consented_at = models.DateTimeField(_("consented at"), default=timezone.now)
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)
    token = models.CharField(
        _("token"), max_length=64, unique=True, default=new_token, editable=False
    )

    class Meta:
        verbose_name = _("newsletter subscriber")
        verbose_name_plural = _("newsletter subscribers")
        ordering = ["-consented_at"]

    def __str__(self):
        return self.email

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None
