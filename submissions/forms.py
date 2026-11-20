from django import forms
from django.utils.translation import gettext_lazy as _

from events.models import Event
from projects.models import Project

from . import spam

EMAIL_HELP = _(
    "Only for questions about your suggestion. Never shown publicly and "
    "never passed on."
)


class SubmissionForm(forms.ModelForm):
    """Common fields: the submitter's email plus the spam checks."""

    # Honeypot: hidden by CSS (`.form-trap`); people leave it empty.
    website = forms.CharField(
        label=_("Leave this field empty"), required=False, max_length=200
    )
    # Signed timestamp; rendered by the template from `started_token`, so it
    # is fresh each time the form is shown (also after errors).
    started = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email = self.fields["submitted_by_email"]
        email.required = True
        email.label = _("Your email")
        email.help_text = EMAIL_HELP
        self.fields["website"].widget.attrs.update(
            {"autocomplete": "off", "tabindex": "-1"}
        )

    def is_spam(self) -> bool:
        """Honeypot filled in: treated as success, but nothing is saved."""
        return bool(self.cleaned_data.get("website"))

    def clean(self):
        cleaned_data = super().clean()
        if spam.filled_in_too_fast(cleaned_data.get("started", "")):
            raise forms.ValidationError(
                _("Please check your entries and send the form again."),
                code="too_fast",
            )
        return cleaned_data

    def save(self, commit=True):
        """Save as an unpublished draft with a first revision, so the
        editor can review and publish it in the admin."""
        obj = super().save(commit=False)
        obj.live = False
        obj.has_unpublished_changes = True
        if commit:
            obj.save()
            obj.save_revision(log_action=True)
        return obj


class EventSubmissionForm(SubmissionForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "start_date",
            "end_date",
            "city",
            "country",
            "link",
            "submitted_by_email",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {"title": _("Name of the event")}


class ProjectSubmissionForm(SubmissionForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "kind",
            "city",
            "country",
            "link",
            "short_description",
            "submitted_by_email",
        ]
        widgets = {"short_description": forms.Textarea(attrs={"rows": 3})}
        help_texts = {
            "link": _("Website or social media page."),
            "short_description": _(
                "One or two sentences: what is it, and how does it carry "
                "Armenian traditions? At most 300 characters."
            ),
        }
