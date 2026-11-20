from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page

from core.seo import SeoPageMixin
from core.themes import Theme
from events.models import Event
from places.models import Place
from projects.models import Project

# Map tiles (ADR 0015), built by scripts/build-map-tiles.sh.
MAP_TILES = "maps/rooterium.pmtiles"


def map_tiles_url() -> str | None:
    """URL of the tile file, or None if it has not been built here."""
    if (Path(settings.MEDIA_ROOT) / MAP_TILES).is_file():
        return settings.MEDIA_URL + MAP_TILES
    return None


class HomePage(SeoPageMixin, Page):
    """Site root: the interactive map (milestone 4)."""

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["stories.ThemeIndexPage"]

    class Meta:
        verbose_name = _("home page")

    def get_page_title(self) -> str:
        # Empty: the home page uses the plain site title (SITE_TITLE).
        return self.seo_title

    def map_features(self, request) -> list[dict]:
        """Markers for the map: live places and upcoming events with
        coordinates. Embedded in the page as JSON."""
        features = []
        places = Place.objects.public().prefetch_related("stories")
        for place in places:
            stories = [s for s in place.stories.all() if s.live]
            story = max(stories, key=lambda s: s.date, default=None)
            features.append(
                {
                    "id": f"place-{place.pk}",
                    "category": place.theme,
                    "categoryLabel": str(Theme(place.theme).label),
                    "name": place.name,
                    "description": place.short_description,
                    "lat": float(place.latitude),
                    "lng": float(place.longitude),
                    "url": story.get_url(request) if story else "",
                    "linkLabel": str(_("Read the story")) if story else "",
                }
            )
        for event in Event.objects.upcoming().filter(latitude__isnull=False):
            features.append(
                {
                    "id": f"event-{event.pk}",
                    "category": "events",
                    "categoryLabel": str(_("Event")),
                    "name": event.title,
                    "description": f"{event.start_date:%d %b %Y} · {event.city}, {event.country}",
                    "lat": float(event.latitude),
                    "lng": float(event.longitude),
                    "url": event.link,
                    "linkLabel": str(_("Event details")),
                }
            )
        return features

    def get_context(self, request, *args, **kwargs):
        from stories.models import StoryPage

        context = super().get_context(request, *args, **kwargs)
        context["map_features"] = self.map_features(request)
        context["map_tiles_url"] = map_tiles_url()
        context["map_filters"] = [
            ("all", _("All")),
            *Theme.choices,
            ("events", _("Events")),
            ("projects", _("Projects")),
        ]
        context["places"] = Place.objects.public().order_by("name")
        context["latest_stories"] = (
            StoryPage.objects.live()
            .select_related("hero_image")
            .order_by("-date", "-pk")[:3]
        )
        context["upcoming_events"] = Event.objects.upcoming()[:3]
        context["projects"] = Project.objects.public()[:4]
        return context
