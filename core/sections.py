"""The page structure of the temple: six section pages and the Symbols
categories (ADR 0018; texts from the editor's design package,
docs/handoff/design-package-2026-11-22.md).

`ensure_sections()` brings any database to this structure and is safe to
run more than once:

1. Section pages of the version 1 themes that no longer exist (Myths,
   Traditions) are migrated: if the target section has no page yet, the
   old page becomes it (new value, title and slug); otherwise its children
   move to the target page and the empty old page is deleted. Wagtail
   creates redirects for the changed URLs (wagtail.contrib.redirects).
2. Missing section pages are created and published, empty fields (root
   symbol, motto) are filled in.
3. Missing Symbols categories are created and published.

Text the editor has written is never overwritten.
"""

from wagtail.models import Page

from core.revisions import latest_version, save_version
from core.themes import LEGACY_THEMES, Theme

SECTIONS = {
    Theme.MUSIC: {"slug": "music", "root_symbol": "duduk"},
    Theme.SYMBOLS: {
        "slug": "symbols",
        "root_symbol": "arevakhach (eternity sign)",
        "motto": "Symbols are the language of memory.",
    },
    Theme.HISTORY: {"slug": "history", "root_symbol": "Ararat, fortress"},
    Theme.ARTIFACTS: {"slug": "artifacts", "root_symbol": "griffin"},
    Theme.PEOPLE: {"slug": "key-people", "root_symbol": "figure with a hidden face"},
    Theme.RELIGION: {"slug": "religion", "root_symbol": "sacred fire"},
}

# The first set of Symbols categories, in order, with what each covers.
SYMBOLS_CATEGORIES = [
    (
        "Eternity and the sun",
        "eternity-and-the-sun",
        "The arevakhach (eternity sign), the wheel of eternity and solar signs.",
    ),
    ("Tree of life", "tree-of-life", "The tree of life and its roots."),
    ("Cross and khachkar", "cross-and-khachkar", "Crosses and cross-stones."),
    ("Pomegranate and grapes", "pomegranate-and-grapes", "Plant symbols."),
    (
        "Beasts and mythical creatures",
        "beasts-and-mythical-creatures",
        "The vishap (dragon stone), the eagle, the lion and the peacock.",
    ),
    ("Ararat", "ararat", "The mountain as a symbol."),
    ("Letters", "letters", "The Armenian alphabet of Mesrop Mashtots."),
    (
        "Knots and ornaments",
        "knots-and-ornaments",
        "Ornaments in carpets, embroidery and stone carving.",
    ),
]


def _publish(page, log, what):
    page.save_revision().publish()
    log(f"  {what}: {page.title}")


def _migrate_legacy(home, log):
    from stories.models import ThemeIndexPage

    for legacy, target in LEGACY_THEMES.items():
        page = ThemeIndexPage.objects.filter(theme=legacy).first()
        if not page:
            continue
        target_page = ThemeIndexPage.objects.filter(theme=target).first()
        if target_page is None:
            version = latest_version(page)
            version.theme = target
            version.title = version.draft_title = str(target.label)
            version.slug = SECTIONS[target]["slug"]
            save_version(version)
            # A draft stays a draft, but the section value must be right at
            # once (the site looks sections up by it).
            ThemeIndexPage.objects.filter(pk=page.pk).update(theme=target)
            log(f"  section {legacy} became: {version.title}")
            continue
        for child in page.get_children():
            child.specific.move(target_page, pos="last-child")
            log(f"  moved to {target_page.title}: {child.title}")
        Page.objects.get(pk=page.pk).delete()
        log(f"  removed the empty {legacy} page")


def _ensure_section_pages(home, log):
    from stories.models import ThemeIndexPage

    pages = {}
    for theme, data in SECTIONS.items():
        page = ThemeIndexPage.objects.filter(theme=theme).first()
        if page is None:
            page = ThemeIndexPage(
                title=str(theme.label), slug=data["slug"], theme=theme
            )
            home.add_child(instance=page)
            for field in ("root_symbol", "motto"):
                setattr(page, field, data.get(field, ""))
            _publish(page, log, "section")
        else:
            version = latest_version(page)
            missing = [
                f
                for f in ("root_symbol", "motto")
                if data.get(f) and not getattr(version, f)
            ]
            if missing:
                for field in missing:
                    setattr(version, field, data[field])
                save_version(version)
                log(f"  section fields ({', '.join(missing)}): {page.title}")
        pages[theme] = page
    return pages


def _ensure_categories(section, log):
    from stories.models import CategoryPage

    for title, slug, intro in SYMBOLS_CATEGORIES:
        if CategoryPage.objects.child_of(section).filter(slug=slug).exists():
            continue
        category = CategoryPage(title=title, slug=slug, intro=intro)
        section.add_child(instance=category)
        _publish(category, log, "category")


def ensure_sections(log=lambda message: None):
    """Bring the page tree to the six sections; returns {Theme: page}."""
    from home.models import HomePage

    home = HomePage.objects.get()
    _migrate_legacy(home, log)
    pages = _ensure_section_pages(home, log)
    _ensure_categories(pages[Theme.SYMBOLS], log)
    return pages


def category(theme, slug):
    """The category page `slug` in the section `theme`, or None."""
    from stories.models import CategoryPage, ThemeIndexPage

    section = ThemeIndexPage.objects.filter(theme=theme).first()
    if section is None:
        return None
    return CategoryPage.objects.child_of(section).filter(slug=slug).first()
