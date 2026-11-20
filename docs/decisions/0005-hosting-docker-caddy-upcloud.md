# 0005: Hosting: Docker Compose, Caddy, UpCloud

- Status: accepted
- Date: YYYY-MM-DD

## Context

Django needs a server with Python and PostgreSQL; shared web hosting is not
enough. Operations should stay simple enough for one person to oversee.

## Decision

- **Hosting:** own VPS at UpCloud, Ubuntu 26.04 LTS, x86_64.
- **Docker Compose** for local development and production
  (services: `caddy`, `web`, `db`).
- **Caddy** as web server/reverse proxy with automatic HTTPS
  (Let's Encrypt); serves uploaded media files directly.
- Django runs under **Gunicorn**; static files are served by WhiteNoise.
- DNS and mail can stay with the existing provider; the site is switched over
  via DNS records.

## Consequences

- One setup for dev and prod, few differences.
- Certificates without manual work.
- We are responsible for server updates, firewall and backups ourselves
  (Ubuntu unattended-upgrades, UFW, ADR 0008).
