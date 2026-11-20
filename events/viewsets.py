from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Event


class EventViewSet(SnippetViewSet):
    model = Event
    icon = "date"
    menu_label = _("Events")
    list_display = ["title", "start_date", "city", "country", "live"]
    list_filter = ["live", "country"]
    search_fields = ["title", "city", "country"]
    search_backend_name = None
    ordering = ["-start_date"]
