# Data model

One section per app with its models, fields and rules (visibility, ordering,
retention). Keep this file in sync with every model change. Decisions behind
it: [ADR 0014](decisions/0014-content-model.md).

> Status: everything below is **built** (milestone 2, issue #2). Placeholder
> content for the prototype: `manage.py seed_demo` (refuses to run with
> `DEBUG` off unless `--allow-production`; safe to run twice).

Conventions: all labels and help texts in English and translatable; every
image is a `CustomImage`; "live" means published in Wagtail (`live=True`).

## `core` – shared

- `core.themes.Theme` (`TextChoices`): `history`, `traditions`, `myths`,
  `symbols`, `music`.
- `core.geo.latitude_field()` / `longitude_field()`: `Decimal(9,6)` with
  range validators.
- Admin menu: "Map & directory" groups places, events and projects
  (`core/wagtail_hooks.py`); "Newsletter" is its own menu item.

## `images` – `CustomImage` (Wagtail image model) – built

`WAGTAILIMAGES_IMAGE_MODEL = "images.CustomImage"`, renditions in
`CustomRendition`.

| Field | Type | Rules |
|---|---|---|
| (Wagtail image fields) | | file, title, focal point, tags, … |
| `description` | text, ≤ 255 | labelled **"Alt text"**, required; Wagtail's own field, used as `default_alt_text` and by `ImageBlock` |
| `credit` | text, ≤ 250 | required; shown under the image, e.g. "Photo: Name" |
| `licence` | text, ≤ 250 | required, e.g. "CC BY-SA 4.0", "With permission" |
| `source_url` | URL | optional |

## `home` – `HomePage` (Wagtail page) – built

Site root, at most one; created by data migration `home.0002` (replaces
Wagtail's welcome page, default `Site` → `localhost`, default site so every
host name matches). Will be the parent of the theme index pages. Map and
teasers come in milestone 4.

## `stories`

### `ThemeIndexPage` (page)

| Field | Type | Rules |
|---|---|---|
| `theme` | `Theme` | required, unique |
| `intro` | text | optional |

Parent: `HomePage`. Children: `StoryPage` only. Lists its live stories,
newest first.

### `StoryPage` (page)

| Field | Type | Rules |
|---|---|---|
| `title` | (Wagtail) | |
| `date` | date | required, default today; shown and used for ordering |
| `teaser` | text, ≤ 300 | required; cards and meta description fallback |
| `hero_image` | `CustomImage` | required, `PROTECT` |
| `body` | StreamField | blocks (`stories/blocks.py`): paragraph (bold, italic, link, lists), heading (h2/h3), quote (text, source, link), image (image, caption), youtube (URL validated to a video ID, title), book_excerpt (text, book title, author, page, link) |
| `related_places` | many-to-many `Place` | optional |

Parent: `ThemeIndexPage` only; no children. Theme = parent's theme
(`story.theme`). Meta description falls back to the teaser, the Open Graph
image is the hero image (1200 × 630). Computed: `reading_time` (220 words
per minute), `more_stories()` (other live stories of the theme). The page
lists its live related places with a link to the home map
(`/?place=place-<id>#explore` selects the marker). The YouTube block is a
two-click embed (`core/static/core/js/video.js`): nothing loads from
YouTube until the visitor clicks.

### `StorySource` (orderable, inline on `StoryPage`)

| Field | Type | Rules |
|---|---|---|
| `title` | text | required, e.g. book or article title |
| `url` | URL | optional |
| `note` | text | optional, e.g. author, page, publisher |

## `places` – `Place` (snippet, draft/publish)

| Field | Type | Rules |
|---|---|---|
| `name` | text | required |
| `theme` | `Theme` | required |
| `latitude` | decimal(9,6) | required, −90…90 |
| `longitude` | decimal(9,6) | required, −180…180 |
| `short_description` | text, ≤ 300 | required, 1–2 sentences |
| `to_be_checked` | bool | default false; seed data sets it; admin filter |

Related stories: reverse of `StoryPage.related_places`. Public: live only.

## `events` – `Event` (snippet, draft/publish)

| Field | Type | Rules |
|---|---|---|
| `title` | text | required |
| `start_date` | date | required |
| `end_date` | date | optional, ≥ `start_date` |
| `city`, `country` | text | required |
| `link` | URL | required |
| `latitude`, `longitude` | decimal(9,6) | optional, both or neither |
| `submitted_by_email` | email | optional, never shown publicly |

Public: live and `(end_date or start_date) >= timezone.localdate()`,
ordered by `start_date`.

## `projects` – `Project` (snippet, draft/publish)

| Field | Type | Rules |
|---|---|---|
| `name` | text | required |
| `kind` | choice | shop, start-up, initiative, music, crafts, other |
| `city`, `country` | text | required |
| `link` | URL | required |
| `logo` | `CustomImage` | optional (credit comes from the image) |
| `short_description` | text, ≤ 300 | required |
| `submitted_by_email` | email | optional, never shown publicly |

Public: live only, ordered by name.

Events and projects can also come from the public "Suggest an event / a
project" forms (`submissions/`): saved with `live=False`, a first
revision (so the editor can publish from the admin) and
`submitted_by_email`. No public uploads: the editor adds coordinates and
logos.

## `newsletter` – `NewsletterSubscriber` (Django model)

| Field | Type | Rules |
|---|---|---|
| `email` | email | unique |
| `consent_text` | text | the consent text shown at signup |
| `consented_at` | datetime | set at signup |
| `confirmed_at` | datetime | null until double opt-in confirmed |
| `token` | text | random, unique; for the confirm and unsubscribe links |

Listed in the Wagtail admin under "Newsletter" (editors: view only, set in
the permissions step; admin URL `/admin/newsletter-subscribers/`).

Double opt-in (`newsletter/signup.py`, `newsletter/views.py`): the sign-up
form (`/newsletter/`, also on the home page) stores the email in lower case,
the consent text as shown and `consented_at`, and emails a confirmation
link. Confirming and unsubscribing happen only on POST (a button on the
linked page), because mail programs open links by themselves. Unsubscribing
deletes the row. Unconfirmed sign-ups older than `UNCONFIRMED_DAYS` (7) are
deleted on every new sign-up and by `manage.py prune_newsletter_signups`
(cron); their confirmation link stops working at the same time. Signing up
again with a confirmed address changes nothing and sends no email; the
visitor sees the same answer either way.

## `pages` – `SimplePage` (Wagtail page) – built

About, Imprint and Privacy (brief, section 2.9), children of the home page,
no subpages.

| Field | Type | Rules |
|---|---|---|
| `purpose` | choice | about, imprint, privacy; unique (each page once) |
| `intro` | text | optional; lead and meta description fallback |
| `body` | rich text | h2, h3, bold, italic, link, lists |

Live pages are linked in the footer in the order About, Imprint, Privacy
(`pages.models.footer_pages`, via the `footer_pages` context variable). The
newsletter and suggestion forms link to the live Privacy page
(`privacy_url`). Not created by a migration: the editor creates them in the
admin with the real texts (issue #14); `seed_demo` creates placeholders
locally. Editors already have page permissions on the whole tree.

## Permissions

Wagtail's "Editors" group: add/edit/**publish** on the page tree, all
permissions on `Place`, `Event`, `Project` (add, change, delete, publish,
view), images and documents, view `NewsletterSubscriber`. Editors are never
superusers.

Granted by data migrations per app (`<app>/migrations/0002_*`, page publish
in `stories/migrations/0002_editors_can_publish_pages.py`) using
`core.permissions.grant()`, which creates missing permissions itself. A new
content model gets its own such migration.
