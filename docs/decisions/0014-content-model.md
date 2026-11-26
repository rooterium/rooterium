# 0014: Content model

- Status: accepted; points 3 and 4 (page tree, theme list) superseded by 0018
- Date: 2026-11-20

## Context

ADR 0009 introduces Wagtail. `docs/PROJECT_BRIEF.md` (section 4) proposes the
content types: stories, theme pages, places, events, projects and newsletter
subscribers. This ADR fixes how they map onto Wagtail and Django, so that the
models in milestone 2 can be built without further decisions. Field-level
details live in [`../data-model.md`](../data-model.md).

## Decision

1. **Wagtail 7.4 LTS** (pinned `>=7.4,<7.5`), the LTS line that pairs with
   Django 5.2 LTS. Upgrades to the next Wagtail LTS are planned together with
   the next Django LTS.
2. **Admin URLs:** the Wagtail admin (for the editor) at `/admin/`, the
   Django admin at `/django-admin/` (technical tasks only).
3. **Page tree:** `HomePage` (site root, one only) → one `ThemeIndexPage`
   per theme → `StoryPage`s. A story's theme is **where it sits in the
   tree**; there is no separate theme field to keep in sync. Moving a story
   to another theme page changes its theme.
4. **Themes are a fixed list in code** (`core.themes.Theme`): History,
   Traditions, Myths, Symbols, Music. Each `ThemeIndexPage` has one of them
   (unique). Places use the same list. "Events" and "Projects" are **map
   filters**, not themes.
5. **Snippets with Wagtail's draft/publish workflow** (`DraftStateMixin`,
   `RevisionMixin`) for `Place`, `Event` and `Project`: the editor gets
   drafts, revisions and an explicit "Publish" instead of a hand-made status
   field. Submissions from the public form (milestone 6) are created as
   drafts. Only live objects are ever shown on the site.
6. **Custom image model** (`images.CustomImage`) from the start, with
   required **alt text** (Wagtail's own `description` field, made required
   and labelled "Alt text"), **credit** and **licence**, plus an optional source
   URL. Every image on the site uses it (hero images, body images, project
   logos).
7. **Story body as StreamField** with these blocks: paragraph (rich text,
   limited features), heading, quote (text, source, optional link), image
   (with optional caption; credit comes from the image), YouTube video (URL,
   validated to a YouTube video ID; rendered via youtube-nocookie.com after a
   click, ADR 0013 – no oEmbed requests), book excerpt (short quote, book
   title, author, optional page and link).
8. **Sources** of a story are an ordered inline list (title, optional URL,
   optional note), not part of the StreamField, so every story has the same
   sources section at the end.
9. **Place ↔ story** links are stored once, on the story
   (`related_places`); the place shows its stories through the reverse
   relation.
10. **Events** are date-based (start date, optional end date), not
    datetime-based. An event is upcoming while its end date (or start date)
    is today or later in `Europe/Vienna` (`timezone.localdate()`).
11. **Coordinates** are decimals with six places (≈ 0.1 m), validated to
    latitude −90…90 and longitude −180…180. Events have optional coordinates
    (both or neither).
12. **Newsletter subscribers** are a plain Django model, visible but not
    editable in the Wagtail admin; the signup flow follows in milestone 7.
    The consent text shown at signup is stored with each subscriber.
13. **Editors** are members of Wagtail's built-in "Editors" group, which
    additionally gets **publish** permission on the page tree and full
    permissions on the snippets (via data migration). The editor publishes
    her own work; there is no separate moderation step in version 1.
14. **SEO** for pages: Wagtail's "SEO title" and "Search description" fields
    feed `page_title` / `meta_description` in `base.html`, falling back to
    the page title and teaser.

## Consequences

- The editor works in one admin with previews, drafts, revisions and
  scheduled publishing for pages and snippets.
- Adding a theme is a code change (choice list + new theme page), which is
  acceptable for five stable themes.
- `title`, `teaser`, `short_description` and the StreamField are ready for
  Wagtail localisation later (ADR 0012); no locale fields are added now.
- Place, event and project URLs are not Wagtail pages; their public views
  are ordinary Django views (milestones 5 and 6).
