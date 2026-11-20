"""Main navigation.

Each feature app adds its entry here once its URLs exist. Entries are
`(label, url_name)` tuples with a translatable label, e.g.
`(gettext_lazy("Events"), "events:list")`; the URL is resolved at render
time. The home page has no entry: the site name in the
header links to it.
"""

from django.utils.translation import gettext_lazy as _

MAIN_NAVIGATION: list[tuple[str, str]] = [
    (_("Stories"), "stories:list"),
    (_("Events"), "events:list"),
    (_("Projects"), "projects:list"),
]
