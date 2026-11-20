# Rooterium

[![CI](https://github.com/rooterium/rooterium/actions/workflows/ci.yml/badge.svg)](https://github.com/rooterium/rooterium/actions/workflows/ci.yml)

Rooterium is a place where Armenian history, traditions, myths, symbols and
music are collected and connected, so that Armenians all over the world – and
anyone curious – can learn about their roots. English first; Armenian and
Russian later.

**Version 1** (details: [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md),
section 2): an interactive map of historic Armenia as the home page, stories
with sources, theme pages, places, events, a directory of projects, a
moderated submission form, a newsletter with double opt-in, and the About,
Imprint and Privacy pages. Status: [`docs/STATUS.md`](docs/STATUS.md).

Built from [`kreuzlin/django-template`](https://github.com/kreuzlin/django-template)
([`docs/NEW_PROJECT.md`](docs/NEW_PROJECT.md)), with Wagtail, MapLibre and an
English, privacy-first setup on top (ADRs 0009–0013).

## Stack

| Area          | Choice                                                   |
|---------------|----------------------------------------------------------|
| Framework     | Django 5.2 LTS, Django templates (no SPA), Wagtail CMS   |
| Frontend      | Plain JS modules / htmx, MapLibre GL JS, self-hosted assets |
| Language      | Python 3.14, dependencies managed with [uv](https://docs.astral.sh/uv/) |
| Lint/format   | Ruff                                                     |
| Database      | PostgreSQL                                               |
| Runtime       | Docker Compose (local and on the server)                 |
| Web server    | Caddy (reverse proxy, automatic HTTPS)                   |
| Hosting       | UpCloud, Ubuntu 26.04 LTS, x86_64                        |
| CI/CD         | GitHub Actions builds `linux/amd64` images, pushed to GHCR |

Rationale: see [`docs/decisions/`](docs/decisions/).

## What is included

- `core` app: base layout, home page, page titles and meta descriptions
  (`core/seo.py`), main navigation, error pages, `/version` (commit of
  the running build)
- Settings from environment variables (`.env.example`), WhiteNoise for static
  files, secure cookies in production
- `compose.yaml` (development), `compose.prod.yaml` + `deploy/Caddyfile`
  (production), `scripts/deploy.sh`, `scripts/backup-db.sh`
- CI: Ruff, Django checks, missing migrations, tests on PostgreSQL, image
  build; push to GHCR from `main` (not from the template repository itself)

## Local development

Requirements: Docker (with the buildx plugin) and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env          # set SECRET_KEY and passwords, never commit .env
docker compose up --build     # start web + PostgreSQL, migrations run automatically
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo   # placeholder content (DEBUG only)
```

Site: <http://localhost:8000> · Wagtail admin (content): <http://localhost:8000/admin/> ·
Django admin (technical): <http://localhost:8000/django-admin/>

The project directory is mounted into the container, so code changes reload
automatically. After changing dependencies (`uv add …`), rebuild with
`docker compose up --build`.

Common tasks:

```bash
docker compose exec web python manage.py test        # tests (inside Docker)
docker compose exec web python manage.py makemigrations
uv run ruff check . --fix && uv run ruff format .    # lint/format (on the host)
docker compose down                                  # stop (data is kept)
docker compose down -v                               # stop and delete the database
```

Inside the container the virtualenv is on `PATH`, so use `python manage.py …`
directly (not `uv run`).

## Documentation

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) – what Rooterium is, scope of version 1, design, milestones
- [`docs/NEW_PROJECT.md`](docs/NEW_PROJECT.md) – setup checklist from the template
- [`docs/STATUS.md`](docs/STATUS.md) – current state, open issues, next steps (start here)
- [`CLAUDE.md`](CLAUDE.md) – working rules for Claude Code (and humans), incl. the session start routine (`/start`) and the merge/deploy rules
- [`docs/architecture.md`](docs/architecture.md) – structure, runtime, delivery
- [`docs/deployment.md`](docs/deployment.md) – server setup, deployments, backups
- [`docs/data-model.md`](docs/data-model.md) – data model
- [`docs/decisions/`](docs/decisions/) – Architecture Decision Records (ADRs)
