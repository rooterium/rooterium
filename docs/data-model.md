# Data model

One section per app with its models, fields and rules (visibility, ordering,
retention). Keep this file in sync with every model change. Decisions behind
it: [ADR 0014](decisions/0014-content-model.md).

> Status: **planned** for milestone 2 (issue #2). Sections move from planned
> to built as the PRs land.

Conventions: all labels and help texts in English and translatable; every
image is a `CustomImage`; "live" means published in Wagtail (`live=True`).

## `core` – shared

- `Theme` (`TextChoices`): `history`, `traditions`, `myths`, `symbols`,
  `music`.

## `images` – `CustomImage` (Wagtail image model)

| Field | Type | Rules |
|---|---|---|
| (Wagtail image fields) | | file, title, focal point, tags, … |
| `alt_text` | text, ≤ 250 | required; describes the image for screen readers |
| `credit` | text, ≤ 250 | required; shown under the image, e.g. "Photo: Name" |
| `licence` | text, ≤ 250 | required, e.g. "CC BY-SA 4.0", "With permission" |
| `source_url` | URL | optional |

## `home` – `HomePage` (Wagtail page)

Site root, at most one. Parent of the theme index pages. Map and teasers
come in milestone 4.

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
| `body` | StreamField | blocks: paragraph, heading, quote, image, youtube, book_excerpt |
| `related_places` | many-to-many `Place` | optional |

Parent: `ThemeIndexPage` only; no children. Theme = parent's theme.

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
| `to_be_checked` | bool | default true for seed data; admin filter |

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

## `newsletter` – `NewsletterSubscriber` (Django model)

| Field | Type | Rules |
|---|---|---|
| `email` | email | unique |
| `consent_text` | text | the consent text shown at signup |
| `consented_at` | datetime | set at signup |
| `confirmed_at` | datetime | null until double opt-in confirmed |
| `token` | text | random, unique; for the confirm and unsubscribe links |

Read-only in the Wagtail admin. Unconfirmed sign-ups older than a set
period are deleted (milestone 7).

## Permissions

Wagtail's "Editors" group: add/edit/**publish** on the page tree, all
permissions on `Place`, `Event`, `Project`, images and documents, view
`NewsletterSubscriber`. Editors are never superusers.
