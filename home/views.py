from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from core.seo import SeoMixin

from .map import map_context


class MapView(SeoMixin, TemplateView):
    """The map of places and events, moved out of the home page (ADR 0017)."""

    template_name = "home/map.html"
    page_title = _("Map")
    meta_description = _(
        "Monasteries, temples, mountains and events on a map of historic "
        "Armenia and the South Caucasus."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(map_context(self.request))
        return context
