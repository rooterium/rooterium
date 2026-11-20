# Rooterium – Project brief (MVP)

Status: agreed starting point for the first prototype, 2026-11-20.
Owner of the idea and content: the founder (referred to as "the editor").
Technical maintainer: Linard (GitHub: kreuzlin).

## 1. What Rooterium is

Rooterium is a place where Armenian history, traditions, myths, symbols and
music are collected and connected, so that Armenians all over the world, and
anyone curious, can learn about their roots.

- **Main audience:** Armenians in the diaspora who grew up in other countries
  and lost touch with their heritage. Everyone is welcome.
- **Success after six months:** people refer to Rooterium as the source where
  they find what they need, or as the start of their journey back to their
  roots.
- **Content:** curated and connected, not only self-produced: own articles,
  plus YouTube videos, articles, book excerpts and links from other sources,
  presented "in a beautiful and interactive way".
- **Rhythm:** one new story about every ten days, written by the editor.
- **Language:** English first. Armenian and Russian later, other languages
  depending on the audience.
- **Organisation:** a personal project for now, possibly an association later.
  Everything must be easy to hand over (see section 9).

## 2. Scope of version 1 (MVP)

In scope:

1. **Home page = interactive map** (design variant B, see section 6).
   - Map of historic Armenia and the South Caucasus with places of interest
     (gold markers).
   - Filter by theme: All, History, Traditions, Myths, Symbols, Music,
     Events, Projects.
   - Selecting a marker shows a card next to the map: theme, name, short
     description, link to the related story.
   - Toggle "Homeland | Diaspora worldwide". Version 1: the diaspora view
     shows a "coming later" message.
   - Below the map: latest stories, newsletter signup.
2. **Stories** (articles) with categories, rich content (text, quotes,
   images with credits, embedded YouTube videos, book excerpts as short
   quotes) and a **sources section** on every story.
3. **Theme pages** listing the stories of one category.
4. **Places** with exact coordinates, linked to stories.
5. **Events**: list of upcoming events (title, date, city, link, optional
   coordinates for the map). Past events disappear automatically.
6. **Projects**: directory of shops, start-ups and initiatives related to
   Armenian culture (name, type, city, link, logo).
7. **Submission form** "Suggest an event / a project": submissions are saved
   as unpublished drafts and the editor is notified by email. Nothing appears
   without her approval. Spam protection without third-party services.
8. **Newsletter signup** with double opt-in and an explicit consent text.
9. **About, Imprint, Privacy** pages (content provided by the editor;
   Austrian imprint/disclosure rules apply while she lives in Austria).

Out of scope for version 1 (later, as GitHub issues with label `later`):
user accounts, comments, forum, contact between users, AI moderation,
translations, the real diaspora world map, an illustrated "theme islands"
map (design variant A).

## 3. Stack and deviations from the template

The repository is created from `kreuzlin/django-template`. Everything in its
CLAUDE.md, CI, deployment and workflow applies, with these deviations (each
gets an ADR in `docs/decisions/`):

- **Wagtail** as CMS on top of Django, so the editor can write stories with
  images and videos comfortably. Content types as Wagtail pages and
  snippets (section 4).
- **MapLibre GL JS** for the map, styled in the Rooterium palette.
  Preference for a map source without third-party tracking, ideally
  self-hosted vector tiles (e.g. a Protomaps PMTiles extract of the region
  served from our own server). Decide and document in an ADR.
- **Interactivity** with plain JavaScript modules or htmx. No React/SPA unless
  an ADR justifies it.
- **Language: English everywhere.** Conversation with the maintainer,
  status reports, `/start` summaries, docs, code, commit messages, admin
  labels and website content are all in English. The template's CLAUDE.md
  (language table, "Session start") and `.claude/commands/start.md` say
  German: change them to English in milestone 1.
- **Locale:** site in English (`LANGUAGE_CODE = "en"`), time
  zone `Europe/Vienna`. All user-facing strings translatable from day one
  (Django i18n; Wagtail localisation prepared, not yet enabled). Fonts and
  layouts must handle Armenian script.
- **Privacy by default (EU audience, GDPR):** no Google Fonts CDN (self-host
  the fonts), YouTube only via youtube-nocookie.com and loaded after a click,
  no analytics in version 1, no third-party scripts without an ADR.

## 4. Content model (proposal, refine in an ADR)

- `StoryPage`: title, theme (category), teaser, hero image (with credit and
  license, required), body as StreamField (paragraph, heading, quote with
  source, image with credit, YouTube embed, book excerpt with source),
  sources (list of title + URL or reference), related places, publish date.
- `ThemeIndexPage`: one per theme, lists its stories.
- `Place` (snippet): name, theme, latitude, longitude, short description
  (1–2 sentences), related stories.
- `Event` (snippet): title, date (and optional end date), city, country,
  link, optional coordinates, status (draft/published), submitted by (email,
  not public).
- `Project` (snippet): name, type (shop, start-up, initiative, music, crafts,
  other), city, country, link, logo (with credit), short description, status,
  submitted by.
- `NewsletterSubscriber`: email, consent timestamp, confirmed timestamp,
  unsubscribe token.
- Every image: alt text and credit/license are required fields.

## 5. Seed data for the prototype

- Five example places with **exact coordinates**, to be verified by the
  editor before going live: Mount Ararat (Symbols), Lake Sevan (History),
  Garni Temple (History), Geghard Monastery (Myths), Gyumri (Traditions).
  Short descriptions as drafts, clearly marked "to be checked".
- Three placeholder stories (titles may be used, body text is placeholder):
  "The eternity sign" (Symbols), "The duduk, voice of apricot wood" (Music),
  "The monastery of the spear" (Myths).
- Placeholder events and projects in square brackets. No invented facts,
  names, dates or statistics anywhere.

## 6. Design

Direction: the discovery of an old, mysterious world, a mix of digital
atlas, historical manuscript and interactive museum. Dark, warm, mysterious,
high quality; minimalist and easy to use, never cluttered or old-fashioned.
Inspiration for the playful map navigation: zig-zag.fm (inspiration only,
do not copy its visuals or wording).

Mockups exist on a Claude design canvas ("Rooterium – Startseiten-Entwürfe",
variant B = "Landkarte"); the maintainer will share screenshots.

### Palette V2 (binding)

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0B0A09` | Page background (dark only, no light theme in v1) |
| `--surface` | `#161311` | Cards, panels |
| `--text` | `#EEE3D1` | Body text, parchment |
| `--text-secondary` | `#C9BFAE` | Teasers, secondary text |
| `--text-muted` | `#8E8B85` | Small meta text (dates, captions) |
| `--muted` | `#7B7872` | Borders and quiet UI only, **not** for small text (4.49:1) |
| `--accent` | `#A6352C` | Pomegranate red: buttons, active states. **Never as text colour** on the background (3:1); light text on it is fine (5.2:1) |
| `--accent-2` | `#D98A3F` | Apricot: links, hover, interactive highlights |
| `--gold` | `#C8A15D` | Antique gold: map markers, connecting lines, symbols, fine ornaments |

Accessibility: WCAG AA (text 4.5:1, large text and UI 3:1), visible focus
rings (apricot), touch targets at least 44 px, everything usable by keyboard,
works on phones (map and side panel stack vertically).

### Typography

- Headings: **Cormorant Garamond** 600, only at 28 px and larger.
- Body and UI: **Manrope** 400–600.
- Armenian script: **Noto Serif Armenian** / **Noto Sans Armenian**.
- All fonts self-hosted (woff2), see privacy rules.

### Images

- `design/` holds the AI-generated mood images (region map, fantasy map,
  moodboard). They are for **atmosphere only** (backgrounds, mood), never as
  illustrations of real objects, symbols or places.
- Real photos need a source and usage rights; credit shown under each image.
- Armenian symbols and script are never AI-generated; they come from
  verified sources.

## 7. Prototype milestones (one or more PRs each)

1. Project setup from the template (docs/NEW_PROJECT.md sections 2 and 3),
   this brief in `docs/`, ADRs for the deviations, issues for all
   milestones.
2. Wagtail integration and content model, admin usable for the editor, seed
   data command.
3. Design foundation: tokens as CSS variables, self-hosted fonts, base
   layout (header, footer, navigation), accessibility basics.
4. Home page with the interactive map (markers, filters, side card,
   homeland/diaspora toggle), mobile layout.
5. Story pages, theme pages, places linked to stories.
6. Events and projects pages, submission form with moderation and email
   notification.
7. Newsletter with double opt-in; About, Imprint, Privacy pages.
8. Deployment to a test server (later, when hosting is decided).

## 8. Open decisions (not blocking the local prototype)

- Domain (e.g. rooterium.com / .org): to be checked and registered.
- Hosting account and who pays (UpCloud, same setup as the template).
- Email sending service for notifications and newsletter.
- Map tile source (ADR in milestone 4).
- Legal entity (association) later.

## 9. Continuity

The platform must outlive any one person's involvement:

- All accounts (domain, server, GitHub, email service) registered to a
  project address, never a private one.
- At least two people with full access (shared password manager).
- GitHub organisation with at least two owners.
- Docs, backups and exportable content as in the template.
