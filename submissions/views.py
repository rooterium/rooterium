from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from core import spam
from core.seo import SeoMixin

from .forms import EventSubmissionForm, ProjectSubmissionForm
from .notify import notify_editor


class SubmissionView(SeoMixin, FormView):
    """Public form: saves a draft, notifies the editor, shows a thank-you
    page. Nothing appears on the site before the editor publishes it."""

    template_name = "submissions/submission_form.html"
    success_url = reverse_lazy("submissions:thanks")
    intro = ""
    back_url_name = ""
    back_label = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["started_token"] = spam.make_started_token()
        context["intro"] = self.intro
        context["back_url"] = reverse_lazy(self.back_url_name)
        context["back_label"] = self.back_label
        return context

    def post(self, request, *args, **kwargs):
        if spam.rate_limited(request, scope="submissions"):
            form = self.get_form()
            form.add_error(
                None,
                _(
                    "You have sent several suggestions in a short time. "
                    "Please try again in an hour."
                ),
            )
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        spam.count_submission(self.request, scope="submissions")
        if not form.is_spam():
            obj = form.save()
            notify_editor(self.request, obj, form.Meta.fields)
        return redirect(self.get_success_url())


class EventSubmissionView(SubmissionView):
    form_class = EventSubmissionForm
    page_title = _("Suggest an event")
    meta_description = _(
        "Know of an Armenian concert, festival or gathering? Suggest it for "
        "the Rooterium events calendar."
    )
    intro = _(
        "Know of a concert, festival, exhibition or gathering? Tell us about "
        "it. The editor checks every suggestion before it appears on the site."
    )
    back_url_name = "events:list"
    back_label = _("Back to the events")


class ProjectSubmissionView(SubmissionView):
    form_class = ProjectSubmissionForm
    page_title = _("Suggest a project")
    meta_description = _(
        "Know a shop, start-up or initiative that carries Armenian traditions "
        "into today? Suggest it for Rooterium."
    )
    intro = _(
        "Know a shop, start-up, music or crafts project that carries Armenian "
        "traditions into today? Tell us about it. The editor checks every "
        "suggestion before it appears on the site."
    )
    back_url_name = "projects:list"
    back_label = _("Back to the projects")


class ThanksView(SeoMixin, TemplateView):
    template_name = "submissions/thanks.html"
    page_title = _("Thank you")
    meta_description = _("Your suggestion has been sent to the editor.")
