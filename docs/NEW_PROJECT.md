# New project from this template

Checklist for everything that does not live in files. Work through it top to
bottom; record what was done (server, DNS, mail) in `docs/STATUS.md` of the
new project. Never write secrets, IP addresses of private machines or
personal data into the repo.

## 1. Create the repository

```bash
gh repo create <owner>/<name> --public --template <owner>/django-template --clone
cd <name>
```

## 2. GitHub settings

Merge options – squash only, the PR title becomes the commit subject,
auto-merge allowed, head branches deleted after the merge:

```bash
REPO=<owner>/<name>
gh repo edit "$REPO" \
  --enable-squash-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --enable-auto-merge \
  --delete-branch-on-merge
gh api -X PATCH "repos/$REPO" \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY
```

Ruleset "protect main" for the default branch (`.github/ruleset-main.json`):
pull request required, **0 approvals** (Claude merges its own PRs), squash
only, **force pushes and deletion blocked**, the CI checks "Lint and test" and
"Build image (linux/amd64)" required, no bypass:

```bash
gh api -X POST "repos/$REPO/rulesets" --input .github/ruleset-main.json
gh api "repos/$REPO/rulesets"
```

From now on every change to `main` goes through a pull request – including
the placeholder replacement below.

- [ ] Merge options set (only squash, PR title, auto-merge, delete branches)
- [ ] Ruleset active (`gh api repos/$REPO/rulesets/<id>` shows all four rules)
- [ ] Issue labels exist: `ops`, `content`, `bug`, `enhancement`
      (`gh label create ops`, …)
- [ ] After the first CI run on `main`: GHCR package
      `ghcr.io/<owner>/<name>` set to **public** (package settings →
      visibility), or the server logs in with a read-only token

## 3. Replace the placeholders

| Placeholder | Example | Used in |
|---|---|---|
| `{{PROJECT_NAME}}` | Full name of the site/organisation | settings, CLAUDE.md |
| `{{PROJECT_SHORT_NAME}}` | Short name for titles and admin | settings |
| `{{SITE_DESCRIPTION}}` | Default meta description (1–2 sentences) | settings |
| `{{LIVE_URL}}` | `https://example.ch` (no trailing slash) | CLAUDE.md, `/start`, docs |
| `{{GITHUB_REPO}}` | `owner/name`, **lower case** | `compose.prod.yaml`, docs |
| `{{PROJECT_SLUG}}` | `name` (directory `/srv/<slug>` on the server) | CLAUDE.md, docs |
| `{{SSH_TARGET}}` | `deploy@<server-ip or host name>` | CLAUDE.md, docs |

On a branch (e.g. `chore/setup-project`):

```bash
grep -rlE '\{\{[A-Z_]+\}\}' --exclude-dir=.git --exclude-dir=.venv --exclude=NEW_PROJECT.md . \
  | xargs sed -i '' \
      -e 's|{{PROJECT_NAME}}|…|g' \
      -e 's|{{PROJECT_SHORT_NAME}}|…|g' \
      -e 's|{{SITE_DESCRIPTION}}|…|g' \
      -e 's|{{LIVE_URL}}|https://…|g' \
      -e 's|{{GITHUB_REPO}}|owner/name|g' \
      -e 's|{{PROJECT_SLUG}}|name|g' \
      -e 's|{{SSH_TARGET}}|deploy@…|g'
grep -rnE '\{\{[A-Z_]+\}\}' --exclude-dir=.git --exclude-dir=.venv --exclude=NEW_PROJECT.md .   # must print nothing
```

(`sed -i ''` is the macOS form; on Linux use `sed -i`.)

Then by hand:

- [ ] `pyproject.toml`: `name = "<name>"`, then `uv lock`
- [ ] `README.md`: replace the template description with the project's
      (purpose, scope of version 1) and the CI badge URL
- [ ] `CLAUDE.md`, "Project context": what the site is for, who maintains it
- [ ] `docs/decisions/`: set the dates of the ADRs, add project-specific ADRs
- [ ] `docs/STATUS.md`: fill in what is already known
- [ ] `site.css`: brand colours from the logo
- [ ] Language and time zone, if the site is not German/Swiss
      (`LANGUAGE_CODE`, `lang` in templates, CLAUDE.md, tests)
- [ ] Delete this template-only line in `CLAUDE.md`
      (`<!-- Template: … -->`)
- [ ] `uv run ruff check . && uv run ruff format --check .`, start locally
      (README) and run the tests; open the PR, let CI pass, merge

## 4. Server at UpCloud

- [ ] UpCloud account with two-factor authentication; billing set up
- [ ] Server: Ubuntu 26.04 LTS, x86_64, at least 1 CPU / 2 GB RAM, location
      close to the visitors; SSH public key added at creation (no password
      login)
- [ ] UpCloud backups: daily, scheduled **after** the 02:00 dump of
      `scripts/backup-db.sh` (ADR 0008); retention noted in `docs/STATUS.md`
- [ ] Server set up according to [`deployment.md`](deployment.md), sections
      1, 3 and 5 (updates, swap, firewall, user `deploy`, SSH hardening,
      Docker, `.env`, cron)
- [ ] `ssh deploy@<server>` works from the maintainer's machine without a
      password prompt (Claude Code deploys through it)
- [ ] Production `.env` stored in the password manager (ADR 0007)
- [ ] IP addresses and access noted in the project's `docs/STATUS.md`

## 5. DNS

- [ ] Before the switch: lower the TTL of the affected records (e.g. 5 min)
- [ ] Test phase: own host name (e.g. `test.<domain>`) or test on the IP
      with `SITE_ADDRESS=:80` (deployment.md, section 3)
- [ ] `A` record(s) → server; `AAAA` only if the server has IPv6 configured;
      remove old `AAAA` records and check wildcard records
- [ ] `MX`, `SPF`, `DKIM`, `DMARC` untouched
- [ ] Check at the authoritative name servers with `dig`, then set
      `SITE_ADDRESS` (Caddy gets the certificate automatically)
- [ ] Go-live: deployment.md, section 8

## 6. Mail

- [ ] Own mailbox for the website as sender (e.g. `website@<domain>`); SMTP
      credentials only in the server `.env`
- [ ] Outbound SMTP from the server allowed on the chosen port (465 or 587);
      some hosters block it for new accounts
- [ ] SPF includes the mail provider; enable **DKIM**; add a **DMARC** record
      (start with `p=none`)
- [ ] `From` is always the site's own address; a visitor's address only as
      `Reply-To`
- [ ] Test: `manage.py sendtestemail <address>` (deployment.md), check the
      headers (SPF/DKIM pass)

## 7. Logo and images

- [ ] Logo as an **original** (vector, e.g. SVG/PDF, or high-resolution PNG)
      in `design/`, not a screenshot or a copy from an old website
- [ ] Web assets (favicon, Open Graph image, header logo) generated from the
      original by a script, not edited by hand
- [ ] For every image: source, author and **usage rights clarified** (own
      photo, license, written permission) and noted, e.g. in
      `design/README.md`
- [ ] Photos showing people (especially children): consent available
- [ ] Every image on the site has an alt text

## 8. After go-live

- [ ] `ROBOTS_TAG=all`, sitemap/Search Console if wanted
- [ ] Uptime monitoring for `{{LIVE_URL}}` and `/version`
- [ ] Keep container images and dependencies up to date (Python base image,
      PostgreSQL, Caddy, `uv lock --upgrade`)
- [ ] Editor accounts for content maintainers (staff, editor group, never
      superusers)
