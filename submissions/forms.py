from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import SpamCheckForm
from events.models import Event
from projects.models import Project

EMAIL_HELP = _(
    "Only for questions about your suggestion. Never shown publicly and "
    "never passed on."
)


class SubmissionForm(SpamCheckForm, forms.ModelForm):
    """Common fields: the submitter's email plus the spam checks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email = self.fields["submitted_by_email"]
        email.required = True
        email.label = _("Your email")
        email.help_text = EMAIL_HELP

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
