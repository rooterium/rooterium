from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import SpamCheckForm

# Stored with every sign-up (as shown, in the visitor's language), so the
# consent can be proven later (ADR 0013).
CONSENT_TEXT = _(
    "Yes, I would like to receive the Rooterium newsletter by email – a new "
    "story about every ten days. My email address is used only for the "
    "newsletter. I can unsubscribe at any time with the link in every email."
)


class SignupForm(SpamCheckForm):
    email = forms.EmailField(
        label=_("Your email"),
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    consent = forms.BooleanField(
        label=CONSENT_TEXT,
        error_messages={
            "required": _("Please confirm that you want to receive the newsletter.")
        },
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
