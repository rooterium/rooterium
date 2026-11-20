"""Wagtail admin menu: places, events and projects grouped together."""

from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from events.viewsets import EventViewSet
from places.viewsets import PlaceViewSet
from projects.viewsets import ProjectViewSet


class MapAndDirectoryGroup(SnippetViewSetGroup):
    items = (PlaceViewSet, EventViewSet, ProjectViewSet)
    menu_icon = "site"
    menu_label = _("Map & directory")
    menu_name = "map-directory"


register_snippet(MapAndDirectoryGroup)
