from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from core import spam
from core.seo import SeoMixin

from .forms import SignupForm
from .models import NewsletterSubscriber
from .signup import subscribe

RATE_SCOPE = "newsletter"


class SignupView(SeoMixin, FormView):
    """Sign-up form (also embedded on the home page, which posts here)."""

    template_name = "newsletter/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("newsletter:check_inbox")
    page_title = _("Newsletter")
    meta_description = _(
        "A new story about Armenian history, traditions, myths, symbols and "
        "music about every ten days – by email."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["started_token"] = spam.make_started_token()
        return context

    def post(self, request, *args, **kwargs):
        if spam.rate_limited(request, scope=RATE_SCOPE):
            form = self.get_form()
            form.add_error(
                None,
                _("Too many sign-ups in a short time. Please try again in an hour."),
            )
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        spam.count_submission(self.request, scope=RATE_SCOPE)
        if not form.is_spam():
            subscribe(self.request, form.cleaned_data["email"])
        return redirect(self.get_success_url())


class CheckInboxView(SeoMixin, TemplateView):
    template_name = "newsletter/check_inbox.html"
    page_title = _("Please check your inbox")
    meta_description = _("Confirm your newsletter sign-up with the link we sent you.")


class TokenView(View):
    """A page with one button, reached from a link in an email.

    The action only happens on POST: mail programs and virus scanners open
    links in emails by themselves, which must not confirm or unsubscribe.
    """

    page_title = ""
    action_template = ""
    invalid_message = ""

    def get_subscriber(self, token):
        return NewsletterSubscriber.objects.filter(token=token).first()

    def invalid(self, request):
        return render(
            request,
            "newsletter/invalid_link.html",
            {
                "page_title": _("This link is no longer valid"),
                "message": self.invalid_message,
            },
            status=404,
        )

    def get(self, request, token):
        subscriber = self.get_subscriber(token)
        if subscriber is None:
            return self.invalid(request)
        return render(
            request,
            self.action_template,
            {"page_title": self.page_title, "subscriber": subscriber},
        )


class ConfirmView(TokenView):
    action_template = "newsletter/confirm.html"
    page_title = _("Confirm your sign-up")
    invalid_message = _(
        "Confirmation links only work for a few days. Please sign up again – "
        "it only takes a moment."
    )

    def get_subscriber(self, token):
        return NewsletterSubscriber.objects.confirmable().filter(token=token).first()

    def post(self, request, token):
        subscriber = self.get_subscriber(token)
        if subscriber is None:
            return self.invalid(request)
        if not subscriber.is_confirmed:
            subscriber.confirmed_at = timezone.now()
            subscriber.save(update_fields=["confirmed_at"])
        return render(
            request,
            "newsletter/confirmed.html",
            {"page_title": _("You are subscribed")},
        )


class UnsubscribeView(TokenView):
    action_template = "newsletter/unsubscribe.html"
    page_title = _("Unsubscribe")
    invalid_message = _(
        "This address is not (or no longer) subscribed. You will not receive "
        "any newsletters."
    )

    def post(self, request, token):
        subscriber = self.get_subscriber(token)
        if subscriber is not None:
            # Data minimisation: nothing is kept after unsubscribing.
            subscriber.delete()
        return render(
            request,
            "newsletter/unsubscribed.html",
            {"page_title": _("You are unsubscribed")},
        )
