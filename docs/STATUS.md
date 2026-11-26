# Project status

Current state of Rooterium and the next steps. **Every PR updates this
file** (at least "Last updated" and whatever the PR changes). Details live in
the linked docs; open work lives in GitHub issues.

_Last updated: 2026-11-26 (PR "Add the temple assets and decisions")_

## Live

- **Test phase on https://rooterium.pocketapp.ch** (a subdomain of the
  maintainer's domain until the final domain is decided, #9). Public, no
  password; `ROBOTS_TAG=noindex, nofollow`.
- The live database holds **example content** (maintainer's request
  2026-11-20: "as accurate and real as possible", to see the real look):
  `seed_demo` placeholders, then `load_example_content --allow-production`
  (`core/example_content.py`). Six stories (Geghard, duduk, eternity sign,
  Garni, khachkars, Ararat) with facts only from the Wikipedia/UNESCO
  pages listed as their sources, 11 photos from Wikimedia Commons (CC BY /
  CC BY-SA, author, licence and source shown under each), eight places
  (coordinates from Wikipedia, still flagged "to be checked"), four real
  recurring events (Armenian Christmas, Trndez, Genocide Remembrance Day,
  Vardavar 2027) and four real organisations as projects (TUMO, Armenia
  Tree Project, Picsart, Komitas Museum-Institute), theme intros and an
  About text. Imprint and Privacy stay placeholders (legal texts). **The
  editor reviews all of it** before the site is announced: texts, the
  choice of projects and events, and whether to keep the photos.
- Map tiles: the maintainer's local build (Protomaps 20261118) copied into
  the `media` volume (`/app/media/maps/rooterium.pmtiles`, checksum
  matched).
- Relief (ADR 0016): Mapterhorn terrain extract (max zoom 8, 22.6 MB)
  copied into the `media` volume (`/app/media/maps/terrain.pmtiles`,
  checksum matched, served by Caddy with range requests), 2026-11-20.

## Temple redesign (version 2, in progress)

On 2026-11-22 the editor delivered a new design package
([`handoff/design-package-2026-11-22.md`](handoff/design-package-2026-11-22.md)):
the site becomes an abandoned temple carved into a cliff, with a portal,
an entrance video, a chapel with six sections and a hall per section. The
maintainer's build brief is [`TEMPLE_BRIEF.md`](TEMPLE_BRIEF.md); it
replaces sections 2 and 6 of the project brief for the home page and the
theme structure. Decisions: ADR 0017 (temple navigation, map moves to
`/map/`), 0018 (six sections, category pages), 0019 (AI assets,
originals, video as Wagtail documents served by Caddy).

| Milestone | State |
|---|---|
| T1 Assets and decisions | **Done** (this PR): ADRs, `design/temple/manifest.json` (21 assets with SHA-256), `build_temple_assets.py` (fetch, build), grain tile `core/static/core/img/grain.png`, issues #57–#65 |
| T2 Content model | Next. Tag `main` as `v1-map` before it merges |
| T3 Visual layer and frame | Open |
| T4 Home journey | Open |
| T5 Section, category and article pages | Open |
| T6 Deploy to the test server | Open |

Notes from T1:

- Originals (69 MB) are on the maintainer's machine in
  `design/temple/originals/` (git-ignored), checked against the manifest.
  The CDN links may expire: keep a copy in the shared storage (#12).
- Videos are encoded at CRF 22 with `-tune grain` instead of the brief's
  CRF 26 (which smoothed the grain); still under 3 MB per clip (portal
  loop 0.4 MB, entrance 2.2 MB, Symbols descent 1.4 MB). Each video's last
  frame matches its still closely, but not pixel for pixel: hold the
  `-last.webp` still after a video, not the PNG it was made from.
- The handoff package was anonymised before committing (file name and
  byline): the editor is not named in the public repo.
- ADR 0019 reads the old rule "Armenian symbols are never AI-generated" as
  "no AI image is the depiction a visitor learns a symbol from": AI
  khachkars appear as scenery in hall headers, never in articles.

## Infrastructure

| What | Where |
|---|---|
| Repository | `github.com/rooterium/rooterium` (public, created from `kreuzlin/django-template`) |
| GitHub settings | Squash merge only (PR title/body), auto-merge allowed, head branches deleted after merge; ruleset "protect main" (id 27710130): PR required (0 approvals), squash only, no force push/deletion, checks "Lint and test" and "Build image (linux/amd64)" required |
| Labels | `ops`, `content`, `bug`, `enhancement`, `later`, `milestone` |
| CI | GitHub Actions: lint + tests, `linux/amd64` image to `ghcr.io/rooterium/rooterium` (`latest`, `sha-<commit>`) on `main`; runs on `main` are queued, never cancelled |
| GHCR package | `ghcr.io/rooterium/rooterium`, **public** (pulled without login) |
| Server | UpCloud, 1 core, 2 GB RAM (+ 2 GB swap), 20 GB disk (can be enlarged, see UpCloud "Increasing storage size"), Ubuntu 26.04.1 LTS, time zone Europe/Vienna, IPv4 `80.47.231.164` (IPv6 not used); who pays: #10 |
| Access | `ssh deploy@80.47.231.164` (SSH key only; root and password login off, `00-hardening.conf`); firewall `ufw`: SSH, 80, 443 |
| App | `/srv/rooterium` (git checkout), `compose.prod.yaml`: `db` (PostgreSQL 18), `web` (GHCR image, Gunicorn), `caddy` (HTTPS) |
| Secrets | `/srv/rooterium/.env` on the server only |
| Backups | cron 02:00 `scripts/backup-db.sh` (dump in `/srv/rooterium/backups`, 14 days; first dump checked) + UpCloud backups daily at 02:15 (enabled by the maintainer, ADR 0008) |
| Cron (`deploy`) | 02:00 database dump, 03:00 `prune_newsletter_signups`; output in `journalctl -t rooterium-cron` |
| Updates | `unattended-upgrades`; automatic reboot at 04:30 when required (`/etc/apt/apt.conf.d/52rooterium-reboot`) |
| Mail | Hostpoint mailbox `rooterium@linard.org` (maintainer's domain; SPF covers Hostpoint, no DMARC policy yet): `asmtp.mail.hostpoint.ch:587`, STARTTLS, PLAIN; sender and editor notifications = this address for now. Helpers on the server: `~/test-smtp-login.sh`, `~/set-mail-password.sh` |
| DNS | Hostpoint (`pocketapp.ch`): `A` record `rooterium` → `80.47.231.164`, no `AAAA` (the zone's wildcard no longer applies to it); final domain: #9 |

Runbook: [`deployment.md`](deployment.md). Architecture:
[`architecture.md`](architecture.md). Decisions: [`decisions/`](decisions/).
Brief and milestones: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md).

## Done (version 1)

- **Milestone 1 – project setup** (#1): GitHub settings and ruleset, labels,
  placeholders replaced (except domain/server), project switched to English
  (`LANGUAGE_CODE = "en"`, `Europe/Vienna`, translatable strings), ADRs
  0009–0013 for the deviations from the template (Wagtail, MapLibre, no SPA,
  English + i18n, privacy by default), issues for all milestones and for
  everything outside version 1 (label `later`), design originals in
  `design/` with `design/README.md`.
- **Milestone 2 – content model decided** (ADR 0014, `docs/data-model.md`).
- **Milestone 2 – Wagtail 7.4 LTS added**: Wagtail admin at `/admin/`,
  Django admin at `/django-admin/`, custom image model with required alt
  text, credit and licence, `HomePage` as site root (data migration).
- **Milestone 2 – content models**: theme pages, stories (StreamField,
  sources, related places), places, events (upcoming filter), projects,
  newsletter subscribers; admin menu "Map & directory" and "Newsletter";
  minimal page templates (designed in milestone 5).
- **Milestone 2 – editor permissions**: Wagtail's "Editors" group can
  publish pages, manage places/events/projects and view newsletter
  subscribers (data migrations).
- **Milestone 2 – seed data**: `manage.py seed_demo` creates the five theme
  pages, five places (flagged "to be checked", issue #15), three
  placeholder stories, three placeholder events and four placeholder
  projects. **Milestone 2 complete.**
- **Milestone 3 – tokens, fonts, base layout**: Palette V2 as CSS
  variables (contrast checked by a test), self-hosted Cormorant Garamond,
  Manrope, Noto Serif/Sans Armenian, header/footer, skip link, focus rings,
  44 px touch targets, mobile layout checked at 390 px.
- **Milestone 3 – web assets**: `design/build_web_assets.py` generates the
  favicons (interim "R" mark, no logo yet) and the default Open Graph
  image.
- **Milestone 3 – Content-Security-Policy** for public pages (own origin
  only, YouTube nocookie frames). **Milestone 3 complete.**
- **Milestone 4 – home page with the map** (ADR 0015): hero, MapLibre map
  with gold button markers, theme/events/projects filters, side card,
  Homeland/Diaspora toggle ("coming later"), place list fallback, latest
  stories, events, projects, newsletter teaser. Checked in Chrome at
  1280 px and 390 px, no CSP violations. Map tiles built locally by the
  maintainer (Protomaps build 20261118, 40 MB, `media/maps/`, not in git);
  style tuned against them (earth tones per land cover, pale glaciers, gold
  shorelines, rivers). Each environment runs `scripts/build-map-tiles.sh`
  once. **Milestone 4 complete.**
- **Milestone 5 – story page**: header with theme link, date, reading
  time; hero image with credit; styled quote, book excerpt, images with
  credit; two-click YouTube embed (youtube-nocookie.com, referrer policy
  set so embeds work); sources; related places with "Show on the map"
  (deep link selects the marker); "More on <theme>"; hero image as Open
  Graph image.
- **Milestone 5 – story overview and theme pages**: `/stories/` (all
  stories, 12 per page) as the first main navigation entry; theme pages
  with intro and story cards; theme chips link to the theme pages (one URL
  per theme). **Milestone 5 complete.**
- **Milestone 6a – events and projects pages**: `/events/` (upcoming
  only, date ranges for multi-day events, "Show on the map" for events with
  coordinates) and `/projects/` (cards with optional logo, filter chips by
  type via `?type=`, filter kept when paginating); both in the main
  navigation after "Stories"; home page sections link to all stories,
  events and projects. Checked at 390 px and 1280 px, no CSP violations.
- **Milestone 6b – submission form** (`submissions/`): `/suggest/event/`
  and `/suggest/project/` (linked from the events and projects pages)
  save unpublished drafts with a first revision and the submitter's email
  (never shown publicly); the editor gets an email with a link to the draft
  in the admin (`EDITOR_NOTIFICATION_EMAIL`; empty = no email, the draft
  still shows up). Spam protection without third parties: honeypot field,
  signed timestamp (at least 3 s, at most 24 h), rate limit of 5 per IP and
  hour (per Gunicorn worker, LocMemCache). Thank-you page at
  `/suggest/thanks/`. Coordinates and logos are added by the editor (no
  public uploads). **Milestone 6 complete.**
- **Milestone 7a – newsletter sign-up** (`newsletter/`): `/newsletter/`
  and a form on the home page (footer link too); stores the consent text as
  shown and its timestamp; confirmation email with a link valid for 7 days;
  confirm and unsubscribe only by button (POST), unsubscribing deletes the
  address; same answer for new, pending and confirmed addresses (no
  enumeration, no email to confirmed ones); unconfirmed sign-ups deleted
  after 7 days (on each sign-up and via `prune_newsletter_signups`, cron in
  `deployment.md`). Spam checks shared with the suggestion forms, moved to
  `core/spam.py` and `core.forms.SpamCheckForm`. Admin URL of the
  subscriber list is now `/admin/newsletter-subscribers/` (the public
  `newsletter` URL namespace needed the name). **Sending** newsletters is
  not built (see open questions).
- **Milestone 7b – About, Imprint, Privacy** (`pages/`): Wagtail page
  type `SimplePage` (purpose unique, intro, rich text) under the home page;
  live ones are linked in the footer; the newsletter and suggestion forms
  link to the Privacy page once it is live. `seed_demo` creates
  placeholder pages locally (the privacy placeholder lists the technical
  facts of the code as a starting point). **Not created in production by a
  migration**: the editor creates and publishes them with the real texts
  (#14) – required before the site goes public. Milestone 7 is complete
  in code; the texts are open.

- **Milestone 8 – first server** (#8, on the server, 2026-11-20): server
  set up per `deployment.md` section 1 (updates and reboot, unattended
  upgrades, swap, `ufw`, user `deploy`, SSH hardening verified, Docker
  29.10 + Compose 5.8 with log limits), repo in `/srv/rooterium`, `.env`
  with the domain, `DEBUG=false`, random `SECRET_KEY` and database password
  (generated on the server, never displayed), first deploy, map tiles
  copied. HTTPS certificate by Caddy, HTTP → HTTPS, headers checked.
  **Incident, fixed:** the first deploy ran while `.env` still had the
  `change-me` secrets (the maintainer's command had not changed them, and
  the deploy did not check); the site was taken offline within minutes,
  the secrets generated, the empty database volume recreated (PostgreSQL
  only takes the password at creation) and the site redeployed. No data or
  accounts existed. Lesson: verify `grep -c change-me .env` is 0 before a
  first deploy (now in the runbook).
- **Server configuration** (on the server, 2026-11-20): crontab for
  `deploy` (database dump 02:00, newsletter cleanup 03:00, output to the
  journal; both run once by hand, first dump 249 KB), automatic reboot at
  04:30 when an update needs it. Memory in use: about 350 MB for the
  containers, 1 GB available; disk 6.7 of 20 GB.
- **Milestone 8 complete** (#8 closed): admin account created and UpCloud
  backups enabled (02:15) by the maintainer; outbound SMTP checked (465
  and 587 open). Mail (#11) and the final domain (#9) are separate issues.
- **Email** (#11, on the server, 2026-11-20): SMTP via Hostpoint. The
  first account (`rooterium@pocketapp.ch`) was refused by Hostpoint with
  `535 Incorrect authentication data` (on 465 and 587, IMAP too); the
  maintainer's mailbox `rooterium@linard.org` works. Hostpoint requires
  port 587 with STARTTLS. Checked live: `sendtestemail`, a newsletter
  sign-up and an event suggestion through the public forms (emails sent
  without errors; subscriber unconfirmed, suggestion an unpublished draft
  with a revision). Delivery confirmed by the maintainer after
  `rooterium@linard.org` was set to forward to their inbox (a change at
  Hostpoint briefly broke the login, then was reverted). Test records
  deleted.

## Open issues

Overview: `gh issue list`. At the time of writing:

| # | Topic | Who |
|---|---|---|
| #1–#6, #8 | Milestones 1–6 and 8 – **closed** | – |
| #7 | M7: newsletter, About/Imprint/Privacy – code done; texts (#14) and real emails (#11) open | Editor / maintainer |
| #9 | Register the final domain (test phase runs on `rooterium.pocketapp.ch`) | Maintainer / editor |
| #10 | Hosting: UpCloud server running; open: who pays | Maintainer / editor |
| #12 | Second GitHub owner, shared password manager | Maintainer / editor |
| #14 | Texts for About, Imprint, Privacy – needed for M7 | Editor |
| #15 | Verify seed place coordinates and descriptions | Editor (after M2) |
| #16–#23 | Outside version 1 (label `later`) | – |
| #57 | Review the temple build's assumptions A1–A15 (after T6) | Editor |
| #58 | Rights for the Higgsfield images and videos – before the announcement | Editor |
| #59 | Portal tagline and chapel heading | Editor |
| #60 | Symbols category covers; hall images and descent videos for the other five sections | Editor |
| #61–#63 | Manuscript menu, article layout in the halls, 9:16 assets (label `later`) | – |
| #64 | Logo | Editor |
| #65 | Armenian name next to the title (`SITE_NATIVE_NAME`) | Editor |

## Next steps

0. **Temple redesign**: milestone T2 (content model) is next, see the
   table above and `docs/TEMPLE_BRIEF.md`, section 9.
1. **Maintainer**: the admin account exists (1 superuser) and UpCloud
   backups run at 02:15. Still open:
   - an editor account in the admin (Settings → Users; staff, group
     "Editors", never superuser) – the group has no members yet;
   - two-factor authentication on the UpCloud account
     (`docs/NEW_PROJECT.md`, section 4);
   - a copy of the production `.env` in the password manager (ADR 0007):
     `ssh deploy@80.47.231.164 'cat /srv/rooterium/.env'` in your own
     terminal, never in a chat.
2. **Editor (#14)**: write and publish About, Imprint and Privacy in the
   admin (Pages → home page → Add child page → "Text page (About, Imprint,
   Privacy)"). The site is public now, so the Imprint is needed soon. The
   Privacy text must cover the newsletter (consent text, 7-day deletion,
   unsubscribe = delete), the submitter email of the suggestion forms,
   YouTube after a click, the email service (#11) and the server logs
   (Caddy access logs on stdout, Docker log limit 10 MB × 5). The local
   placeholder lists these facts. The editor also creates the five theme
   pages before the first story.
3. Email works (#11 closed). The mailbox password stays as it is
   (maintainer's decision, 2026-11-20, although it was sent through the
   chat) – do not raise it again. If it is ever changed at Hostpoint, enter
   it on the server right away with `~/set-mail-password.sh` (sending fails
   in between). Optional for deliverability: DKIM and a DMARC record (`v=DMARC1; p=none`) for the
   sender domain. Set `EDITOR_NOTIFICATION_EMAIL` to the editor's address
   when the editor wants the suggestion emails.
4. Final domain (#9): `A` record, then `SITE_ADDRESS` / `ALLOWED_HOSTS` /
   `CSRF_TRUSTED_ORIGINS` in `.env`, the test subdomain in
   `REDIRECT_ADDRESSES` (permanent redirect), recreate `web` and `caddy`,
   replace the URL in CLAUDE.md, `/start` and the docs.
5. Editor: check the seed place coordinates and descriptions (#15) before
   entering the places in the live admin.

## Session handoff (2026-11-20, second session)

Where the last session stopped: milestones 1–7 merged (PRs #24–#43), no
open PRs, all CI runs green. Update: milestone 8 was completed the same
day – the site runs on https://rooterium.pocketapp.ch (see Live and Done). Milestone 6
(#6) is closed; **#7 is still open** although its code is complete – the
maintainer decides whether to close it (texts are tracked in #14, sending
the newsletter is an open question below). Everything left in version 1
now waits on the maintainer or the editor: final domain (#9) and page
texts (#14). The phone-width review of the live site (390 px, all public
pages) is done: no horizontal scrolling, no console or CSP errors; card
and list links were below 44 px and now the whole card or row is the tap
target (PR "Make whole cards the tap target on phones").

**Design catch-up (done, superseded by the temple redesign above):** the variant B mockup did exist on the
design canvas; it is now in `design/mockup-2b-map.png` (#13 closed). The
live site is being brought in line with it in small PRs: (1) header and
footer – done; (2) home page layout – done: two columns (text, chips and
place card left, map right), container 1360 px, story cards with "All
stories" top right, events/projects with suggest links and project
tiles, one-row newsletter band (shorter consent text), selected chips
in pomegranate; (3) map look – done: relief from elevation data (ADR
0016), glowing markers with name labels. Remaining differences to the
mockup are content (real photos, story texts) and the Armenian name
(`SITE_NATIVE_NAME`, needs the editor).

**Open questions for the maintainer/editor:**

- How will the editor **send** the newsletter? Not part of the brief.
  Options: export the confirmed addresses to the email service chosen in
  #11 (if it has newsletter features), or a simple send function in the
  admin (needs an unsubscribe link per recipient and a List-Unsubscribe
  header). Decide together with #11.
- Armenian word next to the logo (both mockups show "Արմատներ"): set
  `SITE_NATIVE_NAME` in `config/settings.py` once the editor confirms the
  exact wording (brief: Armenian script only from verified sources); #65.
- Footer "a personal project by [Name]": set `SITE_OWNER` in
  `config/settings.py` once the editor agrees to be named. The mockup's
  "Contact" link has no page yet (not in the brief).
- Map: modern political borders are deliberately not shown (ADR 0015);
  the editor decides later whether to show modern or historic borders.
- Real logo: the favicon is an interim "R" mark
  (`design/build_web_assets.py`); #64.

**Before the site is announced** (it is reachable but `noindex`):

- About, Imprint and Privacy written by the editor (#14) – the live
  pages are placeholders from `seed_demo`; all other placeholder content
  replaced or deleted (stories, events, projects, places).
- Editor's address in `EDITOR_NOTIFICATION_EMAIL`; DKIM/DMARC for the
  sender domain.
- Editor account, UpCloud two-factor authentication, `.env` in the
  password manager (next steps, item 1).
- Seed place coordinates checked (#15); final domain (#9); `ROBOTS_TAG`
  switched to `all`.
- Rights for the temple images and videos confirmed (#58); the About page
  says the temple imagery is AI-generated (ADR 0019).

**Local development state** (maintainer's machine, not in git):

- `.env` created from `.env.example` with a random `SECRET_KEY`.
- Map tiles built: `media/maps/rooterium.pmtiles` (Protomaps build
  20261118, 40 MB). Without them the map shows only markers.
- Temple originals in `design/temple/originals/` and web versions in
  `design/temple/web/` (2026-11-26; rebuild with
  `design/temple/build_temple_assets.py fetch` / `build`, needs ffmpeg).
- Database seeded with `seed_demo` (rerun after milestone 7: it now also
  creates placeholder About, Imprint and Privacy pages); the demo story "The monastery of the
  spear" was additionally filled with every block type (placeholders) to
  check the layout.

**Tooling notes for Claude Code sessions:**

- Visual checks: `tools/browser_check.py` (headless Chrome with device
  emulation, console/CSP messages, scripted clicks, YouTube blocked); see
  its docstring. Plain `--headless --window-size` cannot go below 500 px.
- The session's permission rules blocked running downloaded binaries
  (`scripts/build-map-tiles.sh` was run by the maintainer with `!`) and
  force pushes: add follow-up commits instead of amending pushed ones.
- After editing Python files, the dev server's auto-reloader can hang on a
  transient syntax error ("page isn't working"): `docker compose restart web`.
- Local branches of merged PRs still exist (remote ones are deleted).
  Squash merges mean `git branch -d` refuses them; delete with
  `git branch -D <name>` after checking `gh pr list --state merged`.
- Spam checks for public forms are shared: `core/spam.py`,
  `core.forms.SpamCheckForm`, `templates/includes/spam_fields.html`.

## Working agreements (summary)

- English everywhere: conversation, status reports, docs, code, admin and
  site content (ADR 0012). See CLAUDE.md.
- Every change via branch + PR. Claude merges its own PRs with
  `gh pr merge <N> --squash --auto` once the checks are green, verifies with
  `gh pr view` and deploys. PRs with database migrations or server/deployment
  changes are merged by the maintainer – **except until the site goes
  productive: Claude merges those too and may change the server without
  review** (maintainer's decision 2026-11-20, see CLAUDE.md). Never pipe
  `gh` output.
- Content on the live site lives only in the production database, not in
  git; local data is a playground.
