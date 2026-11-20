# 0007: Secrets only in .env

- Status: accepted
- Date: YYYY-MM-DD

## Context

The repository is public or may be shared with more people. Credentials
(Django `SECRET_KEY`, database, SMTP) must never end up in it.

## Decision

- Secrets and environment-specific values live only in `.env`
  (listed in `.gitignore`), loaded via Docker Compose and environment variables.
- The repo contains only `.env.example` with placeholders and explanations.
- Values needed in GitHub Actions are stored as repository secrets.

## Consequences

- Every new variable must be added to `.env.example`.
- The production `.env` exists only on the server and must be backed up
  separately (e.g. in a password manager).
