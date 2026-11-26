# Rooterium: Temple redesign brief (version 2)

Status: working brief, 2026-11-26. Written by the maintainer from the
editor's design package (`docs/handoff/design-package-2026-11-22.md`, "developer
handoff package", 22 Nov 2026). Where the package leaves a question open,
this brief **makes an assumption** (section 2) so the site can be built and
shown on the test server. The editor reviews the result there; every
assumption can be changed afterwards.

This brief **replaces** sections 2 (scope) and 6 (design) of
`docs/PROJECT_BRIEF.md` for the home page and the theme structure. All
other rules stay binding: stack, privacy by default, English everywhere,
accessibility, "no invented facts", continuity, workflow in CLAUDE.md.

## 1. The concept in short

The site is an abandoned temple carved into a cliff (like Geghard). The
home page is its entrance; each section is a hall deep inside. The visitor
walks deeper, toward their roots.

1. **Portal** (first screen): full-screen looping video of the portal in
   the mist, the title ROOTERIUM and an "Enter" hint.
2. **Entrance**: a click plays a 6-second video through the arch into the
   cave chapel.
3. **Chapel**: the last frame stays as a still; the six sections fade in
   over it.
4. **Descent**: picking a section plays a transition into that section's
   hall.
5. **Hall** (section page): the hall image is the header; below it the
   categories (where the section has any) and the articles.

Style: a forgotten memory on old film. Faded grey, green and rose, deep
blacks, grain, scratches, light leaks; one accent colour, pomegranate red.
Faces are hidden. Everything recognisably Armenian. Reference film: *The
Color of Pomegranates* (1969). Details: the handoff package, section
"Visual style".

## 2. Assumptions (the editor may overrule any of them)

| # | Question | Assumption for this build |
|---|---|---|
| A1 | Map, events, projects, newsletter, suggestion forms are not in the package | **Kept, not deleted, but moved out of the journey.** The map moves from the home page to `/map/`. Events, projects, map and newsletter are linked in the footer ("Around the temple"). No code or data is removed. |
| A2 | Six sections instead of five themes | The themes become **Music, Symbols, History, Artifacts, Key people, Religion** (in this order). Traditions and Myths are dropped as sections; existing records are reassigned (section 5). |
| A3 | "No user edits, no moderation" vs. the suggestion forms | The forms stay (they create drafts only the editor publishes, so it is still the team's content). They are reachable from the events and projects pages only. |
| A4 | Section picker in the chapel (manuscript menu A or B, hotspots?) | A **plain list of six links** over the darkened lower part of the chapel still, each with its root symbol as a second line (e.g. "Music · duduk"). No hotspots on the image (they break on phones). Manuscript images 3 and 4 are not used in this build. |
| A5 | Real URLs vs. "the visitor doesn't switch pages" | Every section, category and article has its own URL. The videos are a layer on top: links work, the back button works, a shared link opens the page directly without any intro. |
| A6 | When the intro plays | The portal loop plays on every visit to `/`. The entrance video plays only after a click on "Enter", every time, with a "Skip" button. `/#chapel` opens the chapel still directly (used by "Back to the chapel"). |
| A7 | Sections without a descent video (all except Symbols) | A 1.2 s crossfade from the chapel still to the hall image with a slow zoom. When a descent video exists for a section, it is used instead (no code change, just upload). |
| A8 | Mobile (all assets are 16:9) | Same assets, cropped with `object-fit: cover` and a per-asset focal point. Videos at 720p on all devices. 9:16 versions are a later issue. |
| A9 | Fonts and UI colours | Keep **Cormorant Garamond** (headings, the ROOTERIUM title in spaced capitals) and **Manrope** (body). Keep the Palette V2 tokens for background, text and pomegranate red. **Gold is retired** from the new screens (the package rejects "golden glow"); ornaments and fine lines use a muted parchment tone. A subtle film-grain layer over the whole site; a light flicker only on full-screen video/still screens. |
| A10 | Logo | None yet. The title is set in type; the interim "R" favicon stays. |
| A11 | Hall images and covers for the other five sections | Each section uses its mood board 2 image as hall image: Music 5, History 8, Artifacts 9, Key people 10, Religion 11. Symbols uses the approved khachkar hall image. |
| A12 | Covers for the eight Symbols categories (not made yet) | A category without a cover shows its title on a dark card with the grain texture. Real covers are uploaded later in the admin. |
| A13 | How articles look inside a hall | The existing story page, restyled into the new look (section 7). Symbol pages are ordinary articles: hero image, history, meaning, where it appears as headings in the body. |
| A14 | Images 13 to 17 ("memory flashes", benchmark) | Not used in this build. Images 13 and 14 may serve as covers for the Artifacts section's categories once it has some. |
| A15 | Rights of the Higgsfield images and videos | Assumed usable on the public site under the editor's Higgsfield plan. Must be confirmed by the editor before the site is announced (issue). |

## 3. Rules for AI-generated assets (unchanged principle, made concrete)

- The temple images and videos are **atmosphere**: portal, chapel, hall
  headers, transitions, category covers. They never illustrate a real
  object, symbol, place or person inside an article.
- Articles keep **real, credited photos** (e.g. the Wikimedia Commons
  photos already in the example content). The hero image of the article
  "The eternity sign" is a real photo, not the AI khachkar.
- In the admin, AI images are stored with credit "AI illustration
  (Higgsfield, Soul Cinema)" or "AI video (Higgsfield, Kling 3.0)" and
  licence "Rooterium, see Higgsfield terms". They are not captioned on the
  hall screens; the About page (editor) and `design/README.md` say that the
  temple imagery is AI-generated.
- Mood board 1 (Pinterest references) is **never** used on the site.

## 4. Assets

All approved assets are linked in the handoff package (section "Mood board
2", "Video: first screen loop", "Video: entering the temple", "Section:
Symbols"). Download them at the start: the links are on a third-party CDN
and may expire.

| Key | What | Use |
|---|---|---|
| `img01` … `img17` | Mood board 2 images 1 to 17 | 1 portal poster, 2 chapel still, 5/8/9/10/11 hall images, 3/4/13 to 17 kept for later |
| `hall-symbols` | Khachkar in the dark | Symbols hall image |
| `vid-portal-loop` | 5 s loop, image 1 → image 1 | Portal background |
| `vid-entrance` | 6 s, image 1 → image 2 | Entrance |
| `vid-descent-symbols` | 6 s, image 2 → khachkar | Descent into Symbols |

Handling:

- **Originals are not committed** (about 100 MB). They go to
  `design/temple/originals/` (git-ignored). `design/temple/manifest.json`
  (committed) lists key, source URL, size and SHA-256 of each original, so
  they can be re-downloaded and checked.
- `design/temple/build_temple_assets.py` (or a shell script with ffmpeg)
  produces the web versions into `design/temple/web/` (git-ignored):
  - images: WebP, 1920 px and 960 px wide, quality about 80;
  - videos: H.264 MP4, 1280×720, no audio track, `+faststart`, CRF about
    26 (check size: target under 3 MB per clip); plus a poster (first frame,
    WebP) and a last-frame still (WebP, used to hold the frame);
  - a fine **grain texture** (small tiling PNG, generated with code, not
    AI) for the film-grain layer.
- **Where they live:** images as Wagtail images (`CustomImage`, so the
  editor can replace them); videos as **Wagtail documents** (allow `mp4`
  in `WAGTAILDOCS_EXTENSIONS`, `WAGTAILDOCS_SERVE_METHOD = "direct"` so
  Caddy serves them from the media volume with range requests). Nothing
  large goes into the Docker image. Write an ADR for this (video via
  documents, served by Caddy).
- A management command (e.g. `load_temple_assets <folder>`, same safety
  flag as `load_example_content`) creates or updates the images, documents
  and page fields from the web folder. Locally it runs on
  `design/temple/web/`; on the server the folder is copied over with `scp`
  first.

## 5. Content model changes

- `core.themes.Theme` becomes the six **sections**: `music`, `symbols`,
  `history`, `artifacts`, `people` ("Key people"), `religion` ("Religion"),
  in this order. Rename in code and admin from "theme" to "section" where
  it is visible to the editor; internal names may stay if a rename costs
  more than it helps (decide in the ADR).
- `ThemeIndexPage` → **section page** with new optional fields: root
  symbol (short text, e.g. "duduk"), one-line motto (e.g. "Symbols are the
  language of memory."), hall image (`CustomImage`), descent video
  (document, optional), cover image for the chapel list (optional). Allowed
  children: categories and articles.
- New **category page** (child of a section page): title, intro, cover
  image (optional), order. Children: articles. Generic for all six
  sections; this build creates the eight Symbols categories from the
  package (Eternity and the sun, Tree of life, Cross and khachkar,
  Pomegranate and grapes, Beasts and mythical creatures, Ararat, Letters,
  Knots and ornaments) with their "what it covers" line as intro.
- `StoryPage` (shown as "article" to visitors): parent may be a section or
  a category page. Its section is taken from the nearest section page
  above it.
- `HomePage` gets the journey fields: portal poster image, portal loop
  video, entrance video, chapel still image (all optional; without them
  the home page falls back to the static version, section 6).
- `Place.theme` uses the same six values.
- **Data migration** for existing records: Myths → Religion, Traditions →
  History; then the example content is re-sorted explicitly:
  "The monastery of the spear" → Religion, "The duduk, voice of apricot
  wood" → Music, "The eternity sign" → Symbols / Eternity and the sun,
  "A temple older than Christianity in Armenia" → History (changed
  2026-11-26 so that no section is empty),
  "Khachkars, crosses carved in stone" → Symbols / Cross and khachkar,
  "Ararat, the mountain on the horizon" → Symbols / Ararat. Update
  `core/example_content.py` and `seed_demo` to match, so a fresh database
  gets the same structure. Places follow their stories.
- Keep `docs/data-model.md` in sync.

## 6. Pages and behaviour

### Home page `/`

Server-rendered HTML contains everything; JavaScript adds the journey.

- **Portal screen** (100 svh): `<video autoplay muted loop playsinline
  poster>` of the loop, decorative (`aria-hidden`). Over it: ROOTERIUM as
  the page's `h1`, a one-line tagline (from the home page in the admin;
  placeholder until the editor writes one), and **"Enter"** as a real link
  to `#chapel`. A click anywhere on the portal does the same.
- **Pause control**: the loop runs longer than 5 s, so a visible
  pause/play button is required (WCAG 2.2.2). The choice is remembered for
  the session.
- **Entrance** (JS): on "Enter" the entrance video plays full-screen, once,
  muted, no controls, with a "Skip" button. It is preloaded while the
  portal loop plays. At the end the last frame (the still) stays and the
  chapel content fades in. The URL becomes `/#chapel` (history entry, so
  "back" returns to the portal).
- **Chapel** (`#chapel`): the chapel still as background, a heading
  (e.g. "Choose a path", placeholder wording), the list of six sections
  (A4), each a link to the section page. Sections without live content are
  still listed.
- **Descent** (JS): picking a section plays its descent video (or the
  crossfade, A7) full-screen, then navigates to the section page. The
  section page starts with the same hall image, so the change is seamless.
  Preload the Symbols descent video while the chapel is on screen.
- **Without JavaScript, with `prefers-reduced-motion`, or with
  `navigator.connection.saveData`**: no videos. Portal as still image,
  "Enter" jumps to the chapel section below it, picking a section is a
  normal link.
- Below the chapel, a short footer only (A1). The old home sections
  (latest stories, events, projects, newsletter band) are removed from the
  home page.

### Section page (`/symbols/`, `/music/`, …)

- Header: the hall image full-width (about 100 svh on arrival, the same
  crop as the end of the descent), the section title and the motto fade in
  over it; a scroll hint.
- Below: category cards (cover, title, intro line) if the section has
  categories, then the articles that sit directly in the section.
- "Back to the chapel" link (`/#chapel`).

### Category page

Title, intro, article cards (hero image, title, teaser). Breadcrumb:
Chapel › Section › Category.

### Article (story) page

The existing story page restyled: faded image treatment (a CSS filter on
hero and inline images is fine, never on credits/text), grain layer, the new
header and footer, breadcrumb as above. Content, sources, credits and the
two-click YouTube embed stay as they are.

### Header and footer (all pages except the portal)

- Header: ROOTERIUM (link to `/#chapel`), a "Sections" menu with the six
  sections, nothing else. Mobile: the menu opens as a full-screen list.
- Footer: "Around the temple": Map, Events, Projects, Newsletter; then
  About, Imprint, Privacy (those that are live).

### `/map/`

The current map module and place list, unchanged in function, restyled
lightly to fit (no gold markers: use the parchment tone and pomegranate red
for the selected marker). Story pages' "Show on the map" links point here.

## 7. Visual layer

- Background near-black, text parchment, accent pomegranate red (Palette
  V2 tokens, gold retired per A9). Check contrast with the existing test.
- Film grain: the generated texture as a fixed, non-interactive overlay
  with low opacity, stepped animation; static under reduced motion.
- Full-screen screens (portal, chapel, hall header): vignette and a very
  light flicker (opacity only, under 3 changes per second, no flashing:
  WCAG 2.3.1). Off under reduced motion.
- Transitions: fades and slow zooms only; nothing bright or glossy.
- Cards: no rounded "app" look; thin parchment-tone borders, images with
  the faded treatment.

## 8. Quality bar

- Lighthouse-style basics: the portal poster shows within 1 s on a fast
  connection; total transfer for the first screen under 4 MB (poster +
  loop); the entrance and descent videos are only fetched after the
  portal is shown.
- CSP unchanged (all from our origin). No new third-party requests.
- Keyboard: Enter, Skip, pause, the section list and all links reachable
  and visible with focus rings.
- Checked in the browser (`tools/browser_check.py`) at 1280 px and 390 px,
  with and without reduced motion; no console or CSP errors; screenshots
  of portal, chapel, Symbols hall, a category, an article.
- Tests for: section/category hierarchy and the section lookup, the data
  migration, the home page fallback without assets, the asset loader
  command.

## 9. Milestones (one or more PRs each)

T1. **Assets and decisions** (done, PR "Add the temple assets and decisions"): download originals, `manifest.json`, the
    build script and web versions, the grain texture; ADRs (temple
    navigation replaces the map home page; video as Wagtail documents
    served by Caddy; six sections). Copy the handoff package to
    `docs/handoff/` (done by the maintainer before T1) and update
    `design/README.md`. Issues for everything in section 10.
T2. **Content model** (done, PR "Add sections, category pages and temple fields"): sections, section page fields, category page,
    story parent rules, home page journey fields, data migration, updated
    `seed_demo` / `example_content`, `load_temple_assets`.
T3. **Visual layer and frame** (done, PR "Add the temple frame and move the map to /map/"): tokens (gold retired), grain, header,
    footer, mobile menu, `/map/` moved out of the home page.
T4. **Home journey** (done, PR "Turn the home page into the temple entrance"): portal, pause, entrance, chapel, fallbacks.
T5. **Section, category and article pages** (done, PR "Add the temple halls and the descent"), descent (video and
    crossfade).
T6. **Deploy to the test server** (done 2026-11-26, see `docs/STATUS.md`): copy web assets with `scp`, run
    `load_temple_assets` and the migrations, check the live site at 1280 px
    and 390 px, update `docs/STATUS.md` with screenshots' findings and a
    session handoff. The site is not productive yet, so Claude merges and
    deploys without review (existing agreement).

Before T2 merges, tag the current `main` as `v1-map` so the map version
can be compared or restored.

## 10. Open questions for the editor (create as issues, label `content` or `later`)

- Confirm or change the assumptions A1 to A15 (#57).
- Rights to use the Higgsfield images and videos publicly (A15, #58).
- Tagline on the portal and the chapel heading (#59).
- Covers for the eight Symbols categories; hall images and descent videos
  for Music, History, Artifacts, Key people, Religion (#60).
- Manuscript menu (images 3/4): where, if anywhere (#61).
- Article layout inside halls (audio for Music?) (#62).
- 9:16 versions for phones (#63).
- Logo (#64).
- The Armenian name next to the title (`SITE_NATIVE_NAME`, still open, #65).
