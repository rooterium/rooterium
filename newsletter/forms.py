from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import SpamCheckForm

# Stored with every sign-up (as shown, in the visitor's language), so the
# consent can be proven later (ADR 0013).
CONSENT_TEXT = _(
    "Yes, send me the Rooterium newsletter: a new story about every ten "
    "days. My address is used for nothing else; I can unsubscribe at any "
    "time."
)


class SignupForm(SpamCheckForm):
    email = forms.EmailField(
        label=_("Your email"),
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "placeholder": "your@email.com"}
        ),
    )
    consent = forms.BooleanField(
        label=CONSENT_TEXT,
        error_messages={
            "required": _("Please confirm that you want to receive the newsletter.")
        },
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
