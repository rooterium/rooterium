from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from core.seo import SeoMixin

from .models import Event


class EventListView(SeoMixin, ListView):
    """Upcoming events in date order. Past events disappear by themselves."""

    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 20
    page_title = _("Events")
    meta_description = _(
        "Upcoming Armenian concerts, festivals, exhibitions and gatherings "
        "around the world."
    )

    def get_queryset(self):
        return Event.objects.upcoming()
