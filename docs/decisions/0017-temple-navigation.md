# 0017: Temple navigation replaces the map home page

- Status: accepted
- Date: 2026-11-26

## Context

Version 1 was built around design variant B: the home page is an
interactive map with theme filters, followed by stories, events, projects
and a newsletter band (`docs/PROJECT_BRIEF.md`, sections 2 and 6; ADR 0010,
0015, 0016). On 2026-11-22 the editor delivered a new design package
(`docs/handoff/design-package-2026-11-22.md`): the site is an abandoned temple carved
into a cliff. The home page is its entrance, every section is a hall deep
inside, and the visitor moves through it with short videos. The package
says that the visitor "doesn't switch pages" and leaves the map, events,
projects, newsletter and suggestion forms out.

The maintainer turned the package into `docs/TEMPLE_BRIEF.md`, which makes
assumptions (A1–A15) where the package is open. The editor reviews them on
the test server.

## Decision

1. **Home page = the temple entrance**: portal (looping video, title,
   "Enter"), entrance video, chapel (still image with the list of six
   sections), descent into a section. The map home page and its sections
   (latest stories, events, projects, newsletter band) are removed from `/`.
2. **Real pages under the journey** (A5). Every section, category and
   article has its own URL and is complete server-rendered HTML. The videos
   are a layer added by a JavaScript module (ADR 0011): links, the back
   button and shared links work, and a shared link opens the page directly
   without an intro. `/#chapel` opens the chapel still directly.
3. **When videos play** (A6, A7): the portal loop on every visit to `/`;
   the entrance video only after a click on "Enter", every time, with a
   "Skip" button; a section's descent video when one exists, otherwise a
   1.2 s crossfade from the chapel still to the hall image. Entrance and
   descent videos are fetched only after the portal is on screen.
4. **No videos** without JavaScript, with `prefers-reduced-motion: reduce`
   or with `navigator.connection.saveData`: the portal is a still image,
   "Enter" jumps to the chapel, picking a section is a plain link.
5. **Accessibility**: the portal loop has a visible pause/play button
   (WCAG 2.2.2, choice kept for the session); flicker on full-screen
   screens changes opacity only, less than three times per second
   (WCAG 2.3.1) and is off under reduced motion; "Enter", "Skip", pause and
   the section list are keyboard reachable with visible focus rings; the
   videos are decorative (`aria-hidden`, muted, no audio track).
6. **The map moves to `/map/`** (A1), unchanged in function (ADR 0010,
   0015, 0016 stay valid for it). Its gold markers are restyled in the
   parchment tone with pomegranate red for the selected one. Stories'
   "Show on the map" links point there.
7. **Nothing is deleted** (A1, A3): events, projects, the map and the
   newsletter are linked in the footer under "Around the temple"; the
   suggestion forms stay, reachable from the events and projects pages.
8. **Frame**: the header has the title (link to `/#chapel`) and a
   "Sections" menu, nothing else; full-screen list on phones. Visual layer
   per the temple brief, section 7: Palette V2 for background, text and
   pomegranate red, **gold retired** from the new screens (the package
   rejects "golden glow"; ornaments use a muted parchment tone), a
   film-grain overlay over the whole site (static under reduced motion).
9. The temple brief **replaces sections 2 (scope) and 6 (design)** of
   `docs/PROJECT_BRIEF.md` for the home page and the theme structure; all
   other rules there stay binding. Before the content-model PR (milestone
   T2) merges, the current `main` is tagged `v1-map`.

## Consequences

- The site follows the editor's concept; the map version stays
  reachable at `/map/` and restorable from the `v1-map` tag.
- The first screen is heavier than before (poster plus a short loop,
  budget under 4 MB); videos never block reading because the HTML is
  complete without them.
- The home page no longer surfaces new stories, events or projects; they
  are one click away in the footer. If the editor wants them back on the
  home page, that is a new decision.
- More JavaScript (video orchestration, history entries) to maintain and
  to test with and without reduced motion.
- Every assumption A1–A15 may be overruled by the editor; the changes then
  follow in normal PRs.
