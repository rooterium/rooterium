from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet

from .models import NewsletterSubscriber


class NewsletterSubscriberViewSet(ModelViewSet):
    """Subscribers are listed for the editor; they are created by the
    sign-up flow (milestone 7), not by hand."""

    model = NewsletterSubscriber
    icon = "mail"
    menu_label = _("Newsletter")
    add_to_admin_menu = True
    list_display = ["email", "consented_at", "confirmed_at"]
    list_filter = ["confirmed_at"]
    search_fields = ["email"]
    search_backend_name = None
    form_fields = ["email", "consent_text", "consented_at", "confirmed_at"]
    inspect_view_enabled = True


@hooks.register("register_admin_viewset")
def register_newsletter_viewset():
    return NewsletterSubscriberViewSet("newsletter")
