from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Project


class ProjectViewSet(SnippetViewSet):
    model = Project
    icon = "pick"
    menu_label = _("Projects")
    list_display = ["name", "kind", "city", "country", "live"]
    list_filter = ["kind", "live", "country"]
    search_fields = ["name", "city", "short_description"]
    search_backend_name = None
