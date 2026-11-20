# Architecture

Overview of how the project is built and run. Decisions and their rationale:
[`decisions/`](decisions/). Operations: [`deployment.md`](deployment.md).

## Code

| Path | Purpose |
|---|---|
| `config/` | Settings (one module, configured via environment), URLs, WSGI |
| `core/` | Base layout, SEO (`core/seo.py`), navigation, `/version`, error pages |
| `home/` | Wagtail `HomePage` (site root) |
| `images/` | Wagtail image model with required alt text, credit and licence |
| `stories/` | `ThemeIndexPage`, `StoryPage` (StreamField blocks in `blocks.py`), sources; `/stories/` overview (Django view, paginated) |
| `places/`, `events/`, `projects/` | Snippets with draft/publish; admin viewsets in `viewsets.py`; `/events/` (upcoming only, paginated) and `/projects/` (filter `?type=`, paginated) as Django views |
| `submissions/` | "Suggest an event / a project" forms (`/suggest/…`): drafts, editor notification, spam checks in `spam.py`; no models |
| `newsletter/` | `NewsletterSubscriber` (sign-up flow in milestone 7) |
| `tools/` | Development helpers, not in the image (`browser_check.py`) |

- Wagtail (ADR 0009, 0014): the editor's admin is at `/admin/`, the Django
  admin at `/django-admin/` (technical tasks). Wagtail serves all remaining
  paths (`wagtail_urls` last in `config/urls.py`); feature apps with plain
  Django views are included before it.
- Wagtail's background tasks (search index, reference index) run
  immediately in the request (`django-tasks` default backend); no worker.

- Every public view sets title and meta description via `core.seo.SeoMixin`
  (Wagtail pages: `SeoPageMixin`);
  `base.html` renders `<title>`, description, canonical and Open Graph tags.
- **Content-Security-Policy** (ADR 0013, `core/middleware.py`, policy in
  `settings.CONTENT_SECURITY_POLICY`): public pages may load scripts,
  styles, fonts and images only from our own origin, and frame only
  `youtube-nocookie.com`. `/admin/` and `/django-admin/` are excluded
  (Wagtail's admin needs inline code and frames the page preview), as are
  500 responses (standalone page with inline styles). The map (milestone 4)
  will likely need `worker-src blob:` for MapLibre.
- **Home page map** (ADR 0010, 0015): `home.HomePage.get_context()` embeds
  the markers (live places, upcoming events with coordinates) as JSON;
  `core/static/core/js/map.js` (ES module) loads the vendored MapLibre
  (`core/static/core/vendor/`) and the PMTiles file
  `MEDIA_ROOT/maps/rooterium.pmtiles` (built by
  `scripts/build-map-tiles.sh`, not in git). In development
  `core/dev_media.py` serves media with range requests; in production Caddy
  does. A server-rendered place list is the fallback.
- `/version` returns the Git commit of the running image as JSON
  (`APP_COMMIT`, set by CI); local builds report `dev`.

## Runtime

```
Browser ──HTTPS──▶ caddy ──▶ web (Gunicorn + Django, WhiteNoise for /static/)
                     │              │
                     └─ /media/ ◀───┴── media volume      db (PostgreSQL)
```

- **caddy**: TLS (Let's Encrypt), security headers, redirects of extra host
  names, serves uploaded files from the `media` volume.
- **web**: the image from GHCR, built by CI for `linux/amd64`. Static files
  are collected at build time and served by WhiteNoise.
- **db**: PostgreSQL 18, data in the `postgres_data` volume.

## Delivery

1. Pull request → CI: Ruff, `manage.py check`, missing-migration check,
   tests, image build (no push).
2. Merge to `main` → CI pushes `ghcr.io/rooterium/rooterium:latest` and
   `:sha-<commit>`.
3. `scripts/deploy.sh` on the server pulls the image, runs migrations and
   restarts the containers.

## Backups

Nightly `pg_dump` (`scripts/backup-db.sh`) followed by the UpCloud disk
backup (ADR 0008).
