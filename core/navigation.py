"""Navigation of the temple frame (ADR 0017, temple brief section 6).

- Header: the site name (links to the chapel, `/#chapel`) and a
  "Sections" menu with the six section pages (from the page tree, see
  `core.context_processors`). Nothing else.
- Footer, "Around the temple": the parts of the site outside the journey
  (A1), then About, Imprint and Privacy when they are live.

Entries are `(label, target)` tuples with a translatable label. The target
is a URL name (resolved at render time, e.g. "events:list") or a path
starting with "/" (used as is).
"""

from django.utils.translation import gettext_lazy as _

CHAPEL_URL = "/#chapel"

AROUND_THE_TEMPLE: list[tuple[str, str]] = [
    (_("Map"), "map"),
    (_("Events"), "events:list"),
    (_("Projects"), "projects:list"),
    (_("Newsletter"), "newsletter:signup"),
]
