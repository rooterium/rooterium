"""Shared form parts for public forms."""

from django import forms
from django.utils.translation import gettext_lazy as _

from core import spam


class SpamCheckForm(forms.Form):
    """Honeypot and minimum fill time (`core.spam`). Combine with a
    ModelForm via multiple inheritance; render the two fields with
    `{% include "includes/spam_fields.html" %}` and pass `started_token`
    (`spam.make_started_token()`) into the template context."""

    # Honeypot: hidden by CSS (`.form-trap`); people leave it empty.
    website = forms.CharField(
        label=_("Leave this field empty"), required=False, max_length=200
    )
    # Signed timestamp; rendered by the template from `started_token`, so it
    # is fresh each time the form is shown (also after errors).
    started = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"].widget.attrs.update(
            {"autocomplete": "off", "tabindex": "-1"}
        )

    def is_spam(self) -> bool:
        """Honeypot filled in: treat as success, but save nothing."""
        return bool(self.cleaned_data.get("website"))

    def clean(self):
        cleaned_data = super().clean()
        if spam.filled_in_too_fast(cleaned_data.get("started", "")):
            raise forms.ValidationError(
                _("Please check your entries and send the form again."),
                code="too_fast",
            )
        return cleaned_data

    def user_fields(self):
        """Visible fields without the honeypot, for templates."""
        return [f for f in self.visible_fields() if f.name != "website"]
