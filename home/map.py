"""The map of places and events (ADR 0010, 0015, 0016), at /map/ since the
temple redesign (ADR 0017). Shared by the map view and, until milestone T4,
the home page."""

from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.themes import Theme, theme_label
from events.models import Event
from places.models import Place
from projects.models import Project

# Map tiles (ADR 0015) and terrain for the relief (ADR 0016), built by
# scripts/build-map-tiles.sh.
MAP_TILES = "maps/rooterium.pmtiles"
MAP_TERRAIN = "maps/terrain.pmtiles"


def media_file_url(path: str) -> str | None:
    """URL of a file in MEDIA_ROOT, or None if it has not been built here."""
    if (Path(settings.MEDIA_ROOT) / path).is_file():
        return settings.MEDIA_URL + path
    return None


def map_tiles_url() -> str | None:
    return media_file_url(MAP_TILES)


def map_features(request) -> list[dict]:
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
                "categoryLabel": theme_label(place.theme),
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


def map_context(request) -> dict:
    return {
        "map_features": map_features(request),
        "map_tiles_url": map_tiles_url(),
        "map_terrain_url": media_file_url(MAP_TERRAIN),
        "map_filters": [
            ("all", _("All")),
            *Theme.choices,
            ("events", _("Events")),
            ("projects", _("Projects")),
        ],
        "places": Place.objects.public().order_by("name"),
        "upcoming_events": Event.objects.upcoming()[:3],
        "projects": Project.objects.public()[:4],
    }
