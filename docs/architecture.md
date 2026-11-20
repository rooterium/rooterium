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
| `stories/` | `ThemeIndexPage`, `StoryPage` (StreamField blocks in `blocks.py`), sources |
| `places/`, `events/`, `projects/` | Snippets with draft/publish; admin viewsets in `viewsets.py` |
| `newsletter/` | `NewsletterSubscriber` (sign-up flow in milestone 7) |

- Wagtail (ADR 0009, 0014): the editor's admin is at `/admin/`, the Django
  admin at `/django-admin/` (technical tasks). Wagtail serves all remaining
  paths (`wagtail_urls` last in `config/urls.py`); feature apps with plain
  Django views are included before it.
- Wagtail's background tasks (search index, reference index) run
  immediately in the request (`django-tasks` default backend); no worker.

- Every public view sets title and meta description via `core.seo.SeoMixin`
  (Wagtail pages: `SeoPageMixin`);
  `base.html` renders `<title>`, description, canonical and Open Graph tags.
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
