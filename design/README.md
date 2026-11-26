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

## Temple assets (`design/temple/`)

The images and videos of the temple design (ADR 0017, 0019;
`docs/TEMPLE_BRIEF.md`) come from the editor's design package
(`docs/handoff/design-package-2026-11-22.md`). **They are AI-generated** (Higgsfield:
Soul Cinema for the stills, Kling 3.0 for the videos) and are used as
atmosphere only: portal, chapel, hall headers, transitions, category
covers. They never illustrate a real object, symbol, place or person in an
article; articles use real, credited photos. Rights: assumed usable under
the editor's Higgsfield plan, to be confirmed before the site is announced
(#58).

- `manifest.json` (committed): every approved asset with key, title,
  intended use, generator, source URL, size and SHA-256.
- `originals/` (git-ignored, about 69 MB): the downloaded originals.
- `web/` (git-ignored, about 8 MB): generated web versions.

```bash
uv run python design/temple/build_temple_assets.py fetch   # download + check
uv run python design/temple/build_temple_assets.py build   # web versions (needs ffmpeg)
```

| Key | What | Use in this build |
|---|---|---|
| `img01` | Temple portal in the cliff, mist | Portal poster |
| `img02` | Cave chapel, woman in taraz | Chapel still |
| `img05`, `img08`, `img09`, `img10`, `img11` | Music, History, Artifacts, Key people, Religion | Hall images of those sections |
| `hall-symbols` | Khachkar in the dark | Symbols hall image |
| `vid-portal-loop` | 5 s loop, portal to portal | Portal background |
| `vid-entrance` | 6 s, portal to chapel | Entrance |
| `vid-descent-symbols` | 6 s, chapel to khachkar | Descent into Symbols |
| `img03`, `img04`, `img06`, `img07`, `img12`–`img16` | Manuscript menu, alternative Symbols and Religion images, griffins, memory flashes | Kept for later |
| `img17` | Style benchmark | Not used |

Web versions: images as WebP (quality 80, 1920 px and 960 px wide, never
upscaled); videos as H.264 1280×720 without audio (CRF 22, `-tune grain`,
each under 3 MB), each with a poster (`-poster.webp`, first frame) and the
last frame (`-last.webp`, held as a still when the video ends). The script
also writes the film-grain tile `core/static/core/img/grain.png` (generated
noise, committed). In a database the web versions become Wagtail images
and documents via `load_temple_assets` (milestone T2).

Adding an asset (e.g. a descent video for another section): add an entry
to `manifest.json` without `bytes`/`sha256`, run `fetch --record`, then
`build`.

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

From `docs/PROJECT_BRIEF.md`, section 6, and ADR 0019:

- AI-generated images are for **atmosphere only**, never as illustrations of
  real objects, symbols or places. The objects in them (khachkars, carpets,
  instruments, buildings) are not accurate depictions.
- No AI image is ever the depiction a visitor learns an Armenian symbol
  from: a khachkar in a hall header is scenery, the article about it shows
  a real photo. Armenian script is never AI-generated; it comes from
  verified sources.
- Mood board 1 of the editor's package (other people's photos and film
  stills) is never used on the site.
- Real photos need a source, author and clarified usage rights, recorded in
  this table; the credit is shown under each image on the site.
- The design canvas "Rooterium – Startseiten-Entwürfe" (the maintainer's
  claude.ai account) holds the boards A, B and the style board; variant B
  is the reference for version 1. Export a board as PNG into this folder
  when it changes.
