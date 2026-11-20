"""Main navigation.

Layout from the variant B mockup (design/mockup-2b-map.png): Map,
Stories, Events, Projects, then About (a Wagtail page, added in
`core.context_processors` when it is live) and the Subscribe button.

Entries are `(label, target)` tuples with a translatable label. The target
is a URL name (resolved at render time, e.g. "events:list") or a path
starting with "/" (used as is). The site name in the header links home.
"""

from django.utils.translation import gettext_lazy as _

MAIN_NAVIGATION: list[tuple[str, str]] = [
    (_("Map"), "/#explore"),
    (_("Stories"), "stories:list"),
    (_("Events"), "events:list"),
    (_("Projects"), "projects:list"),
]
