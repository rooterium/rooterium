# Data model

One section per app with its models, fields and rules (visibility, ordering,
retention). Keep this file in sync with every model change. Decisions behind
it: [ADR 0014](decisions/0014-content-model.md), sections and categories:
[ADR 0018](decisions/0018-six-sections-and-categories.md), temple assets:
[ADR 0019](decisions/0019-temple-assets-and-video.md).

> Status: everything below is **built** (milestone 2, issue #2). Placeholder
> content for the prototype: `manage.py seed_demo` (refuses to run with
> `DEBUG` off unless `--allow-production`; safe to run twice). Example
> content with real photos and checked facts on top of it:
> `manage.py load_example_content` (same flag; data in
> `core/example_content.py`, photos from Wikimedia Commons with author,
> licence and source; replaces only `[placeholder]` objects).
>
> Temple redesign (milestone T2): `manage.py restructure_sections` brings a
> version 1 page tree to the six sections and creates the Symbols
> categories (`core/sections.py`; no flag, it is structural);
> `manage.py load_temple_assets <folder>` loads the temple images and videos
> (`core/temple_assets.py`; `--allow-production` like the others).

Conventions: all labels and help texts in English and translatable; every
image is a `CustomImage`; "live" means published in Wagtail (`live=True`).

## `core` – shared

- `core.themes.Theme` (`TextChoices`): the six **sections**, in chapel
  order: `music`, `symbols`, `history`, `artifacts`, `people` ("Key
  people"), `religion`. Internally still called "theme" (`Theme`,
  `ThemeIndexPage`, the `theme` fields); the admin and the site say
  "section" (ADR 0018). `LEGACY_THEMES` maps the version 1 values
  (`myths` → `religion`, `traditions` → `history`); `theme_label()` shows
  a label for any stored value.
- `core.sections`: the section pages' default root symbols and motto, the
  eight Symbols categories, `ensure_sections()`.
- `core.revisions`: `latest_version()` / `save_version()` – code that fills
  in page fields starts from the editor's draft and never publishes it.
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
host name matches). Parent of the section pages and the text pages (About,
Imprint, Privacy). Shows the map, latest stories, upcoming events, projects
and the newsletter sign-up (`HomePage.get_context()`) until the temple
journey replaces it (ADR 0017, milestone T4).

Temple entrance fields (admin panel "Temple entrance"), all optional:

| Field | Type | Rules |
|---|---|---|
| `tagline` | text, ≤ 200 | one line under the title on the portal (#59) |
| `portal_poster` | `CustomImage` | still of the portal; shown while the loop loads and instead of videos |
| `portal_video` | document (MP4) | looping portal video |
| `entrance_video` | document (MP4) | played after "Enter", ends on the chapel |
| `chapel_heading` | text, ≤ 100 | heading over the section list (#59) |
| `chapel_image` | `CustomImage` | chapel still behind the section list (the entrance video's last frame) |

Images and videos are `SET_NULL` on delete.

## `stories`

### `ThemeIndexPage` (page) – "section page" in the admin

| Field | Type | Rules |
|---|---|---|
| `theme` | `Theme` | required, unique; labelled "section" |
| `intro` | text | optional |
| `root_symbol` | text, ≤ 60 | optional, e.g. "duduk"; second line in the chapel list |
| `motto` | text, ≤ 200 | optional, one line over the hall image |
| `hall_image` | `CustomImage` | optional; full-width header of the section |
| `descent_video` | document (MP4) | optional; without it the chapel crossfades into the hall image |
| `cover_image` | `CustomImage` | optional; for the chapel list |

Parent: `HomePage`. Children: `CategoryPage` and `StoryPage`. Lists its
live categories (page order) and the live stories directly below it,
newest first. Slugs: the value, except `people` → `key-people`.

### `CategoryPage` (page)

| Field | Type | Rules |
|---|---|---|
| `title` | (Wagtail) | |
| `intro` | text | optional; what the category covers |
| `cover_image` | `CustomImage` | optional; without it the card shows the title |

Parent: `ThemeIndexPage`. Children: `StoryPage`. Order = page order in the
section. Generic for all sections; Symbols has eight from the design
package (`core.sections.SYMBOLS_CATEGORIES`).

### `StoryPage` (page)

| Field | Type | Rules |
|---|---|---|
| `title` | (Wagtail) | |
| `date` | date | required, default today; shown and used for ordering |
| `teaser` | text, ≤ 300 | required; cards and meta description fallback |
| `hero_image` | `CustomImage` | required, `PROTECT` |
| `body` | StreamField | blocks (`stories/blocks.py`): paragraph (bold, italic, link, lists), heading (h2/h3), quote (text, source, link), image (image, caption), youtube (URL validated to a video ID, title), book_excerpt (text, book title, author, page, link) |
| `related_places` | many-to-many `Place` | optional |

Parent: `ThemeIndexPage` or `CategoryPage`; no children. Section = the
nearest `ThemeIndexPage` above it (`story.theme_page`, `story.theme`);
`story.category` is the category page or `None`. Meta description falls back to the teaser, the Open Graph
image is the hero image (1200 × 630). Computed: `reading_time` (220 words
per minute), `more_stories()` (other live stories anywhere in the
section). The page
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
| `theme` | `Theme` | required; labelled "section" (`places.0004` moved Myths → Religion, Traditions → History, revisions included) |
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
superusers. The page types added later (`CategoryPage`) are covered by the
tree permissions; no extra migration.

## Documents (Wagtail's own model)

PDFs and MP4 videos (`WAGTAILDOCS_EXTENSIONS`), served directly from
`MEDIA_ROOT/documents/` (`WAGTAILDOCS_SERVE_METHOD = "direct"`, ADR 0019):
Caddy in production, `core.dev_media` locally, both with range requests.
Every document is public by its URL. The temple images and videos live in
the collection "Temple".

Granted by data migrations per app (`<app>/migrations/0002_*`, page publish
in `stories/migrations/0002_editors_can_publish_pages.py`) using
`core.permissions.grant()`, which creates missing permissions itself. A new
content model gets its own such migration.
