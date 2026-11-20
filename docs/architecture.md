# Architecture

Overview of how the project is built and run. Decisions and their rationale:
[`decisions/`](decisions/). Operations: [`deployment.md`](deployment.md).

## Code

| Path | Purpose |
|---|---|
| `config/` | Settings (one module, configured via environment), URLs, WSGI |
| `core/` | Base layout, home page, SEO (`core/seo.py`), navigation, `/version`, error pages |
| `<app>/` | One small Django app per topic (added per project) |

- Every public view sets title and meta description via `core.seo.SeoMixin`;
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
2. Merge to `main` → CI pushes `ghcr.io/{{GITHUB_REPO}}:latest` and
   `:sha-<commit>`.
3. `scripts/deploy.sh` on the server pulls the image, runs migrations and
   restarts the containers.

## Backups

Nightly `pg_dump` (`scripts/backup-db.sh`) followed by the UpCloud disk
backup (ADR 0008).
