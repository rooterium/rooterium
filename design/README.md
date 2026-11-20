# Design originals

Originals for the website's images. Not served and not part of the Docker
image; web assets are generated from them by a script:

```bash
uv run python design/build_web_assets.py
```

It writes to `core/static/core/img/` (commit the result):

| File | From |
|---|---|
| `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`, `icon-512.png` | Interim mark: gold "R" in Cormorant Garamond in a thin gold ring – **until a real logo exists** |
| `og-default.jpg` (1200 × 630) | `rooterium_v2_region_map.png` darkened, with site name and tagline; default Open Graph image |

| File | What | Source and rights | Use |
|---|---|---|---|
| `rooterium_v2_region_map.png` | Stylised relief map of the region | AI-generated mood image | Atmosphere only (backgrounds, mood); background of `og-default.jpg` |
| `rooterium_v2_fantasy_map.png` | Fantasy map with theme islands | AI-generated mood image | Atmosphere only |
| `rooterium_v2_moodboard.png` | Moodboard (khachkar, pomegranate, carpet, duduk, …) | AI-generated mood image | Reference for colour and mood only |
| `mockup-2a-theme-islands.png` | Home page mockup, design variant A ("Themen-Inseln") | Screenshot of the Claude design canvas "Rooterium – Startseiten-Entwürfe" | Reference only; variant A is out of scope for version 1 (issue #23) |
| `mockup-2b-map.png` | Home page mockup, design variant B ("Landkarte"), 1440 px | Screenshot of the same canvas, board "B · Landkarte" | **The agreed design for version 1**: header, home page layout, map look, cards, newsletter band, footer |

## Fonts

Self-hosted woff2 files in `core/static/core/fonts/` (ADR 0013), taken from
the Fontsource npm packages 5.3.0, each under the SIL Open Font License 1.1
(licence files next to the fonts):

| Font | Use | Subsets |
|---|---|---|
| Cormorant Garamond 600 | Headings ≥ 28 px | latin, latin-ext |
| Manrope (variable, 200–800) | Body and UI | latin, latin-ext |
| Noto Serif Armenian (variable) | Armenian in headings | armenian |
| Noto Sans Armenian (variable) | Armenian in body text | armenian |

Cyrillic subsets are added together with the Russian translation.

## Rules

From `docs/PROJECT_BRIEF.md`, section 6:

- AI-generated images are for **atmosphere only**, never as illustrations of
  real objects, symbols or places. The objects in them (khachkars, carpets,
  instruments, buildings) are not accurate depictions.
- Armenian symbols and script are never AI-generated; they come from verified
  sources.
- Real photos need a source, author and clarified usage rights, recorded in
  this table; the credit is shown under each image on the site.
- The design canvas "Rooterium – Startseiten-Entwürfe" (the maintainer's
  claude.ai account) holds the boards A, B and the style board; variant B
  is the reference for version 1. Export a board as PNG into this folder
  when it changes.
