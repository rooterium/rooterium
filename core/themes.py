"""The fixed list of sections (ADR 0014, changed by ADR 0018).

Internally they are still called "themes" (`Theme`, `ThemeIndexPage`, the
`theme` fields); everything the editor and visitors see says "section".
Stories get their section from the nearest section page above them; places
have it as a field. "Events" and "Projects" are map filters, not sections.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.TextChoices):
    """The six sections of the temple, in the order of the chapel list."""

    MUSIC = "music", _("Music")
    SYMBOLS = "symbols", _("Symbols")
    HISTORY = "history", _("History")
    ARTIFACTS = "artifacts", _("Artifacts")
    PEOPLE = "people", _("Key people")
    RELIGION = "religion", _("Religion")


# Values of the version 1 themes that are no longer sections, and the
# section their records move to (ADR 0018, temple brief A2).
LEGACY_THEMES = {"myths": Theme.RELIGION, "traditions": Theme.HISTORY}


def theme_label(value: str | None) -> str:
    """The section's label; tolerant of legacy values not yet migrated."""
    if not value:
        return ""
    if value in LEGACY_THEMES:
        return str(LEGACY_THEMES[value].label)
    try:
        return str(Theme(value).label)
    except ValueError:
        return value
