# Project status

Current state of Rooterium and the next steps. **Every PR updates this
file** (at least "Last updated" and whatever the PR changes). Details live in
the linked docs; open work lives in GitHub issues.

_Last updated: 2026-11-20 (PR "Set up Rooterium from the template")_

## Live

- **Not live yet.** No domain and no server (issues #8–#10). The placeholders
  `{{LIVE_URL}}` and `{{SSH_TARGET}}` are deliberately still in CLAUDE.md,
  `/start` and `docs/deployment.md`; replace them in milestone 8.
- Deployed commit: — (nothing deployed). Development happens locally.
- Search engines: test phase will use `ROBOTS_TAG=noindex, nofollow`.

## Infrastructure

| What | Where |
|---|---|
| Repository | `github.com/rooterium/rooterium` (public, created from `kreuzlin/django-template`) |
| GitHub settings | Squash merge only (PR title/body), auto-merge allowed, head branches deleted after merge; ruleset "protect main" (id 27710130): PR required (0 approvals), squash only, no force push/deletion, checks "Lint and test" and "Build image (linux/amd64)" required |
| Labels | `ops`, `content`, `bug`, `enhancement`, `later`, `milestone` |
| CI | GitHub Actions: lint + tests, `linux/amd64` image to `ghcr.io/rooterium/rooterium` (`latest`, `sha-<commit>`) on `main`; runs on `main` are queued, never cancelled |
| GHCR package | Created by the first CI run on `main`; **then set to public** (or the server uses a read-only token) – not done yet |
| Server | _Not decided_ (template default: UpCloud, Ubuntu 26.04, time zone Europe/Vienna) – issue #10 |
| Access | `ssh {{SSH_TARGET}}` – once a server exists |
| App | `/srv/rooterium` (git checkout), `compose.prod.yaml`: `db` (PostgreSQL 18), `web` (GHCR image, Gunicorn), `caddy` (HTTPS) |
| Secrets | `/srv/rooterium/.env` on the server only |
| Backups | cron 02:00 `scripts/backup-db.sh` + provider backup – once a server exists |
| Mail | _Not decided_ – issue #11 |
| DNS | _No domain yet_ – issue #9 |

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

## Open issues

Overview: `gh issue list`. At the time of writing:

| # | Topic | Who |
|---|---|---|
| #2–#8 | Milestones 2–8 (label `milestone`) | Claude / maintainer |
| #9 | Register the domain | Maintainer / editor |
| #10 | Hosting account and who pays | Maintainer / editor |
| #11 | Email sending service | Maintainer |
| #12 | Second GitHub owner, shared password manager | Maintainer / editor |
| #13 | Mockups of design variant B ("Landkarte") – needed for M4 | Maintainer |
| #14 | Texts for About, Imprint, Privacy – needed for M7 | Editor |
| #15 | Verify seed place coordinates and descriptions | Editor (after M2) |
| #16–#23 | Outside version 1 (label `later`) | – |

## Next steps

1. Maintainer merges this PR (it touches `compose.prod.yaml`, so it is a
   maintainer-merge exception); afterwards set the GHCR package to public.
2. Milestone 2 (#2): Wagtail integration and content model, editor group,
   seed data command.
3. Milestone 3 (#3): design foundation (Palette V2 tokens in `site.css`,
   self-hosted fonts incl. Armenian, base layout). The template's
   `site.css` still has the neutral template colours until then.

## Working agreements (summary)

- English everywhere: conversation, status reports, docs, code, admin and
  site content (ADR 0012). See CLAUDE.md.
- Every change via branch + PR. Claude merges its own PRs with
  `gh pr merge <N> --squash --auto` once the checks are green, verifies with
  `gh pr view` and deploys. PRs with database migrations or server/deployment
  changes are merged by the maintainer. Never pipe `gh` output.
- Content on the live site lives only in the production database, not in
  git; local data is a playground.
