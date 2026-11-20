# CLAUDE.md

Guidelines for working on this repository (Rooterium; test phase on
https://rooterium.pocketapp.ch, see `docs/STATUS.md`).
Applies to Claude Code and human contributors.

## Session start

Every new session first works out the current state itself – the
conversation history of earlier sessions is not available. Run `/start`
(`.claude/commands/start.md`) or do the same by hand:

1. `git status --short` (uncommitted changes? ask before switching), then
   `git switch main && git pull`.
2. Read `docs/STATUS.md` – current state, infrastructure, open issues, next
   steps.
3. `git log --oneline -15`
4. `gh pr list --state open`
5. `gh issue list --state open`
6. `gh run list --limit 10` (failed or cancelled runs on `main`?)
7. Live version: `curl -s https://rooterium.pocketapp.ch/version` and compare
   with `git rev-parse origin/main`.

Report the result to the maintainer in English before starting new work.

## Project context

- Rooterium collects and connects Armenian history, traditions, myths,
  symbols and music, so that Armenians all over the world – above all in the
  diaspora – and anyone curious can learn about their roots. The founder
  ("the editor") owns the idea and writes the content; the technical
  maintainer runs the platform. Full brief: `docs/PROJECT_BRIEF.md`.
- Live on https://rooterium.pocketapp.ch (test phase, `noindex`; the final
  domain is still open, issue #9). Server: UpCloud, `ssh deploy@80.47.231.164`.
  DNS changes are done by the maintainer.
- Content is maintained through the Wagtail admin (ADR 0009) – it must be
  understandable for non-technical users (clear English `verbose_name`s,
  help texts, sensible list views and filters).
- Scope of version 1: `docs/PROJECT_BRIEF.md`, section 2. No features beyond
  that without asking; ideas for later go into issues labelled `later`.

## Stack (binding)

- Django 5.2 LTS with Django templates, **Wagtail** as CMS (ADR 0009).
- Interactivity with plain JavaScript modules or htmx (ADR 0011). No
  React/SPA, no frontend build step unless an ADR justifies it.
- Map: **MapLibre GL JS**, self-hosted (ADR 0010).
- Privacy by default (ADR 0013): no third-party requests from the browser
  (fonts self-hosted, YouTube only via youtube-nocookie.com after a click, no
  analytics); a new third-party script needs an ADR.
- Python dependencies only via **uv** (`pyproject.toml`, `uv.lock`).
  No `pip install`, no `requirements.txt`.
- **Ruff** for linting and formatting.
- **PostgreSQL** – also locally, no SQLite.
- **Docker Compose** for development and production.
- Production: UpCloud, Ubuntu 26.04 LTS, Caddy (automatic HTTPS).
- GitHub Actions builds images for `linux/amd64` (development happens on
  Apple Silicon, the server is x86).

Rationale lives in `docs/decisions/`. To deviate, write a new ADR first.

## Language

| What                                                        | Language |
|-------------------------------------------------------------|----------|
English everywhere (ADR 0012):

| What                                                        | Language |
|-------------------------------------------------------------|----------|
| Conversation with the maintainer, status reports, `/start`  | English  |
| Website content, templates (user-facing text), admin labels, form and error messages | English (translatable) |
| Documentation (README, CLAUDE.md, docs/, ADRs)              | English  |
| Code: identifiers, comments, docstrings, commit messages    | English  |

- `LANGUAGE_CODE = "en"`, `TIME_ZONE = "Europe/Vienna"`, `USE_TZ = True`.
- Every user-facing string is translatable from day one: `{% translate %}` /
  `{% blocktranslate %}` in templates, `gettext_lazy` in Python. Armenian and
  Russian come later (issue #21); Wagtail localisation is prepared, not
  enabled.
- Fonts and layouts must handle Armenian script.

## Workflow

- **Pull requests.** The default branch is `main`. Never commit or push
  directly to `main`.
  - Each step gets its own branch from an up-to-date `main`, named
    `<type>/<short-description>` (e.g. `feat/events`, `fix/contact-form`,
    `docs/…`, `chore/…`).
  - Push the branch and open a PR against `main` with `gh pr create`; the PR
    description (English) explains what changed and how it was tested.
  - `main` is protected by the ruleset "protect main" that only allows
    **squash merges**. The PR title becomes the commit message on `main`, so
    write it as a good commit subject (English, imperative, e.g. "Add events
    calendar").
  - The ruleset also requires the CI checks "Lint and test" and
    "Build image (linux/amd64)" to pass before a PR can be merged. If a job
    is renamed in `.github/workflows/ci.yml`, update the ruleset as well.
  - Repository settings: **auto-merge is allowed** and **head branches are
    deleted automatically** after the merge.
- **Merging – Claude merges its own PRs**, except in the cases below:
  1. `gh pr merge <N> --squash --auto`. With green checks GitHub merges
     right away; otherwise the PR is queued and merges once the checks pass.
  2. Check the result with
     `gh pr view <N> --json state,mergedAt,autoMergeRequest`: `state` is
     `MERGED`, or `autoMergeRequest` is set (queued – wait with
     `gh pr checks <N> --watch`, then check again). Anything else means the
     merge did not happen – report it, do not deploy.
  3. Deploy (see below) and report the result.
  - **Exceptions – the maintainer merges these PRs.** Open the PR, say in the
    PR description and in the chat why it is an exception, and stop:
    - the PR contains a **database migration** (any file in a `migrations/`
      directory), or
    - the PR changes the **server or the deployment**: `compose.prod.yaml`,
      `Dockerfile`, `deploy/`, `scripts/`, `.github/workflows/`, new or
      changed variables in `.env.example`, or anything that needs manual
      steps on the server (`.env`, cron, packages).
  - If the PR is already merged, say so and skip the merge command.
- **Deploying** (after Claude's own merge, if the PR changes the app):
  1. Wait until CI on `main` has pushed the image for the merge commit:
     `gh run list --branch main --limit 1`, then `gh run watch <run-id>`.
  2. `ssh deploy@80.47.231.164 'cd /srv/rooterium && scripts/deploy.sh'`
  3. `curl -s https://rooterium.pocketapp.ch/version` must show the merge
     commit; `curl -s -o /dev/null -w "%{http_code}\n"
     https://rooterium.pocketapp.ch/` must be `200`.
  - Docs- or CI-only changes need no deploy (the live commit then lags behind
    `main`). If CI or the deploy fails, report it and stop – no retries that
    change the server.
- **Do not pipe `gh` output** through `tail`, `head`, `grep` or similar, and
  do not hide its stderr: errors and hints from `gh` must stay visible.
- **Small steps.** Commit after every working step (tests green, Ruff clean).
  Keep PRs small – one step of the plan per PR. Keep migrations in their own
  PR where possible, so the rest can be merged without waiting.
- Before committing: `uv run ruff check . && uv run ruff format --check .` and
  `docker compose exec web python manage.py test`.
- Tests cover the most important behaviour (e.g. visibility rules, forms incl.
  spam protection, page titles and meta descriptions).
- Keep docs in sync: model changes → `docs/data-model.md`, architecture or
  operations changes → `docs/architecture.md` / `docs/deployment.md`,
  fundamental decisions → new ADR in `docs/decisions/`.
- **Every PR updates `docs/STATUS.md`**: at least "Last updated", plus what
  the PR changes (state, open issues, next steps). Work done directly on the
  server (content, `.env`, deploys) is recorded there too, in the next PR.
- Open work is tracked as GitHub issues (labels `ops`, `content`, `bug`,
  `enhancement`); reference them in PRs (`Fixes #N`).

## Secrets

- Secrets only in `.env` (never committed). The repo contains only
  `.env.example` with placeholders and comments.
- Every new environment variable is documented in `.env.example` at the same time.
- No passwords, tokens or personal data in code, tests, fixtures or docs.
- Secrets are entered on the server by the maintainer, never passed through
  chat, issues or the repo.

## Conventions

- Small, topic-focused Django apps (e.g. `posts`, `events`, `contact`).
- Every public page sets `<title>` and `<meta name="description">`: views use
  `core.seo.SeoMixin` (`page_title`, `meta_description`), Wagtail pages
  `core.seo.SeoPageMixin` (SEO title / search description); the base template
  renders title, description, canonical and Open Graph tags, falling back to
  `SITE_TITLE` / `SITE_DESCRIPTION` from settings.
- Templates extend `base.html`. New sections get a main navigation entry in
  `core/navigation.py`.
- Styles live in `core/static/core/css/site.css` (plain CSS, no framework),
  colours as CSS variables on `:root` (Palette V2; contrast pairs are
  checked by `core/tests/test_design_tokens.py`). Cormorant Garamond only
  for headings of 28 px and more; everything else Manrope. Touch targets at
  least 44 px (`--touch`), visible apricot focus rings. Accent colours are for accents only;
  text must meet contrast requirements (use `--text-muted` for secondary
  text). Errors must not rely on colour alone.
- Logo and image originals live in `design/` (not served, not in the image);
  web assets are generated from them by a script, not edited by hand. Only
  use images whose usage rights are clear.
- Never render user content with `|safe`.
- Public templates have **no inline scripts, inline styles or `style=`
  attributes**: the Content-Security-Policy blocks them (ADR 0013). JS
  goes into static ES modules, data into `<script type="application/json">`
  or `data-` attributes. A new external source needs an ADR and an entry in
  `CONTENT_SECURITY_POLICY`.
- Images always use the Wagtail image model `images.CustomImage` (required
  alt text, credit, licence); never a plain `ImageField`.
- Editors are staff users in an editor group (never superusers). A new
  content model gets its permissions for that group via a data migration.
- Uploaded files (images, PDFs) live under `MEDIA_ROOT` on a Docker volume;
  static files are collected during the image build.
- Time logic (e.g. "past events") uses `django.utils.timezone.now()`, never
  naive datetimes.

## Useful commands

```bash
docker compose up --build                            # dev environment
docker compose exec web python manage.py <command>   # manage.py inside Docker
docker compose exec web python manage.py test
uv run ruff check . --fix
uv run ruff format .
```

- Visual check of a page (phone widths, console and CSP messages, clicks):
  `uv run --no-project --with websockets python tools/browser_check.py URL OUT.png --width 390`.
- Map tiles for local development (once): `scripts/build-map-tiles.sh`.
- Inside the container use `python manage.py`, not `uv run` (the venv is
  at `/opt/venv` and on `PATH`; `uv run` would try to sync dev dependencies).
- `compose.yaml` is the development setup; `compose.prod.yaml` is production
  (Caddy + GHCR image, see `docs/deployment.md`).
