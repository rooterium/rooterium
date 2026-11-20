# Project status

Current state of {{LIVE_URL}} and the next steps. **Every PR updates this
file** (at least "Last updated" and whatever the PR changes). Details live in
the linked docs; open work lives in GitHub issues.

_Last updated: YYYY-MM-DD (PR "…")_

## Live

- **{{LIVE_URL}}** – not live yet. _When live: since when, which host names
  redirect there._
- Deployed commit: `curl -s {{LIVE_URL}}/version`, compare with
  `git rev-parse origin/main`. Last deploy: `—`. Docs- or CI-only changes
  need no deploy (the live commit then lags behind `main`).
- Search engines: _`ROBOTS_TAG` value (test phase: `noindex, nofollow`)._

## Infrastructure

| What | Where |
|---|---|
| Server | UpCloud, Ubuntu 26.04, _IPv4 / IPv6_, time zone Europe/Zurich |
| Access | `ssh {{SSH_TARGET}}` (key only, no root login, passwordless sudo) |
| App | `/srv/{{PROJECT_SLUG}}` (git checkout), `compose.prod.yaml`: `db` (PostgreSQL 18), `web` (GHCR image, Gunicorn), `caddy` (HTTPS) |
| Secrets | `/srv/{{PROJECT_SLUG}}/.env` on the server only |
| Deploy | `scripts/deploy.sh` on the server after CI has pushed the image for the merged commit |
| Backups | cron 02:00 `scripts/backup-db.sh` (14 days in `backups/`), UpCloud backup _daily at …_ |
| Cron | _scheduled jobs_ |
| Mail | _SMTP provider, sender address_ |
| DNS | _DNS provider, records pointing to the server_ |
| CI | GitHub Actions: lint + tests, `linux/amd64` image to `ghcr.io/{{GITHUB_REPO}}` (`latest`, `sha-<commit>`) on `main`; runs on `main` are queued, never cancelled |

Runbook: [`deployment.md`](deployment.md). Architecture:
[`architecture.md`](architecture.md). Decisions: [`decisions/`](decisions/).

## Done (version 1)

- _Nothing yet._

## Open issues

Overview: `gh issue list`. At the time of writing:

| # | Topic | Who |
|---|---|---|
| | | |

## Next steps

1. _…_

## Working agreements (summary)

- Conversation with the maintainer in German; docs and code in English; site
  content German (Swiss spelling). See CLAUDE.md.
- Every change via branch + PR. Claude merges its own PRs with
  `gh pr merge <N> --squash --auto` once the checks are green, verifies with
  `gh pr view` and deploys. PRs with database migrations or server/deployment
  changes are merged by the maintainer. Never pipe `gh` output.
- Content on the live site lives only in the production database, not in
  git; local data is a playground.
