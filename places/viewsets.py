from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Place


class PlaceViewSet(SnippetViewSet):
    model = Place
    icon = "site"
    menu_label = _("Places")
    list_display = ["name", "theme", "to_be_checked", "live"]
    list_filter = ["theme", "to_be_checked", "live"]
    search_fields = ["name", "short_description"]
    search_backend_name = None
