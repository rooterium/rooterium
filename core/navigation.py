"""Main navigation.

Each feature app adds its entry here once its URLs exist. Entries are
`(label, url_name)` tuples, e.g. `("Kontakt", "contact:form")`; the URL is
resolved at render time. The home page has no entry: the site name in the
header links to it.
"""

MAIN_NAVIGATION: list[tuple[str, str]] = []
