"""Main navigation.

Each feature app adds its entry here once its URLs exist. Entries are
`(label, url_name)` tuples with a translatable label, e.g.
`(gettext_lazy("Events"), "events:list")`; the URL is resolved at render
time. The home page has no entry: the site name in the
header links to it.
"""

MAIN_NAVIGATION: list[tuple[str, str]] = []
