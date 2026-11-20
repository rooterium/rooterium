# Django template

Template for small content websites with Django, PostgreSQL and Docker
Compose, deployed to a single server with Caddy. Includes working rules for
Claude Code (`CLAUDE.md`, `/start`), CI that builds `linux/amd64` images,
deploy and backup scripts, and a minimal Django app with tests.

**New project:** use this repository as a template, then follow
[`docs/NEW_PROJECT.md`](docs/NEW_PROJECT.md) (GitHub settings, placeholders,
server, DNS, mail, images).

## Stack

| Area          | Choice                                                   |
|---------------|----------------------------------------------------------|
| Framework     | Django 5.2 LTS, Django templates (no SPA)                |
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
  (`core/seo.py`), main navigation, German error pages, `/version` (commit of
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
```

Site: <http://localhost:8000> · Admin: <http://localhost:8000/admin/>

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

- [`docs/NEW_PROJECT.md`](docs/NEW_PROJECT.md) – checklist for a new project
- [`docs/STATUS.md`](docs/STATUS.md) – current state, open issues, next steps (start here)
- [`CLAUDE.md`](CLAUDE.md) – working rules for Claude Code (and humans), incl. the session start routine (`/start`) and the merge/deploy rules
- [`docs/architecture.md`](docs/architecture.md) – structure, runtime, delivery
- [`docs/deployment.md`](docs/deployment.md) – server setup, deployments, backups
- [`docs/data-model.md`](docs/data-model.md) – data model
- [`docs/decisions/`](docs/decisions/) – Architecture Decision Records (ADRs)
