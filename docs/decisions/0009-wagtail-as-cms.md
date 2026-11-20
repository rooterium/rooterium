# 0009: Wagtail as CMS

- Status: accepted
- Date: 2026-11-20

## Context

ADR 0002 makes the Django admin the editing interface. Rooterium's content is
different from a typical small site: the editor writes long stories with
images, quotes, embedded videos, book excerpts and a sources section, about
one every ten days. She is not technical. In the Django admin, rich and
structured content like this would need a lot of custom widgets.

## Decision

- Use **Wagtail** (current LTS release that supports Django 5.2) on top of
  Django. The Wagtail admin is the editing interface for content; the Django
  admin stays available for technical tasks only.
- Stories are Wagtail **pages** with a **StreamField** body (paragraph,
  heading, quote with source, image with credit, YouTube embed, book excerpt
  with source). Theme index pages are pages too.
- Places, events, projects are Wagtail **snippets**. Newsletter subscribers
  stay a plain Django model (not editorial content).
- Images use a **custom image model** with required alt text and
  credit/licence fields.
- Editors are members of Wagtail's editor group, never superusers.
- The exact content model is refined in an ADR in milestone 2 (issue #2);
  `docs/data-model.md` follows it.
- Wagtail localisation (`wagtail.contrib.simple_translation` /
  `WAGTAIL_I18N_ENABLED`) is prepared but not enabled in version 1 (ADR 0012).

## Consequences

- The editor gets page previews, drafts, revisions, scheduled publishing,
  an image library with focal points and a rich text editor out of the box.
- One more large dependency to keep up to date; Wagtail and Django upgrades
  have to be planned together (Wagtail LTS ↔ Django LTS).
- Wagtail brings its own admin UI (React-based internally); this does not
  affect the public site, which stays server-rendered (ADR 0011).
- Wagtail's search uses the database backend (PostgreSQL); no Elasticsearch.
