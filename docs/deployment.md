# Deployment and operations

How the production server runs {{LIVE_URL}}. Architecture and rationale:
[`architecture.md`](architecture.md), ADRs 0005–0008. Placeholders in
examples: `<server-ip>`, `<domain>`.

## Overview

- UpCloud server, Ubuntu 26.04 LTS, Docker Engine with the Compose plugin.
- Repo checkout in `/srv/{{PROJECT_SLUG}}` (public repo, no credentials
  needed). It provides `compose.prod.yaml`, `deploy/Caddyfile` and the
  scripts; the app itself comes as an image from GHCR.
- `.env` in `/srv/{{PROJECT_SLUG}}` holds all secrets (mode `600`, never
  committed).
- Containers: `db` (PostgreSQL 18), `web` (Gunicorn), `caddy` (HTTPS).

## 1. Server setup (once)

As root on a fresh server:

```bash
# Updates, automatic security updates (enabled by default once installed)
apt update && apt upgrade -y
apt install -y ufw unattended-upgrades git ca-certificates curl
# reboot if /var/run/reboot-required exists

# Time zone (cron times below are Swiss time)
timedatectl set-timezone Europe/Zurich

# Swap as a safety net (small servers have ~2 GB RAM)
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo "/swapfile none swap sw 0 0" >> /etc/fstab
echo "vm.swappiness=10" > /etc/sysctl.d/99-swappiness.conf && sysctl -p /etc/sysctl.d/99-swappiness.conf

# Firewall
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 443/udp
ufw enable

# Admin user with SSH key login (copies root's authorized_keys).
# No password, so sudo without password – the docker group is
# root-equivalent anyway.
adduser --disabled-password --gecos "" deploy
usermod -aG sudo deploy
echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy && chmod 440 /etc/sudoers.d/deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Docker publishes ports past `ufw`; only Caddy publishes ports (80/443), so
this is fine – never publish the database or `web`.

SSH hardening: first check that `ssh deploy@<server-ip>` and `sudo -n true`
work in a second session. Then create
`/etc/ssh/sshd_config.d/00-hardening.conf` (the `00-` prefix matters: sshd
uses the first value it reads, and `50-cloud-init.conf` may enable
passwords), run `sshd -t && systemctl reload ssh` and verify with `sshd -T`:

```
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
```

From now on log in as `deploy`. Install Docker Engine from Docker's apt
repository (docs.docker.com, "Install Docker Engine on Ubuntu"), then
`usermod -aG docker deploy` and limit container log size in
`/etc/docker/daemon.json`, then `systemctl restart docker`:

```json
{
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "5"}
}
```

## 2. DNS

At the DNS provider: an `A` record (and `AAAA` only if the server has IPv6
configured) for the site's host name pointing to the server. Caddy can only
obtain the certificate once this record resolves. Watch out for wildcard
records and existing `AAAA` records that point elsewhere – they make some
clients reach the old host. Never touch `MX`, `SPF`, `DKIM` or `DMARC`
records as part of the website.

Check the authoritative name servers directly (bypasses local caches):

```bash
dig +short <domain> A @<authoritative-name-server>
dig +short <domain> AAAA @<authoritative-name-server>
```

## 3. First deployment

As `deploy`:

```bash
sudo mkdir -p /srv/{{PROJECT_SLUG}} && sudo chown deploy:deploy /srv/{{PROJECT_SLUG}}
git clone https://github.com/{{GITHUB_REPO}}.git /srv/{{PROJECT_SLUG}}
cd /srv/{{PROJECT_SLUG}}
cp .env.example .env && chmod 600 .env
```

Edit `.env` for production:

| Variable | Value |
|---|---|
| `SECRET_KEY` | new random key (see comment in `.env.example`) |
| `DEBUG` | `false` |
| `ALLOWED_HOSTS` | `<domain>` |
| `CSRF_TRUSTED_ORIGINS` | `https://<domain>` |
| `SITE_ADDRESS` | `<domain>` (`:80` for a test on the IP, see below) |
| `REDIRECT_ADDRESSES` | e.g. `www.<domain>`, or empty |
| `ROBOTS_TAG` | `noindex, nofollow` (test phase), `all` when live |
| `POSTGRES_PASSWORD` | new random password, same in `DATABASE_URL` |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP server and the website's own mailbox |

Secrets are entered on the server by the maintainer, never passed through
chat, issues or the repo. Put passwords in **single quotes**
(`EMAIL_HOST_PASSWORD='...'`): Docker Compose interpolates `$` in unquoted
values. A password can be written without echoing it, e.g. with
`read -rsp "Passwort: " PW` and a small script that updates `.env`.

**Before DNS points to the server**, test over plain HTTP on the IP: set
`SITE_ADDRESS=:80`, leave `REDIRECT_ADDRESSES` empty and add the IP to
`ALLOWED_HOSTS`. Do not set the domain earlier – Caddy would keep failing the
ACME challenge and can hit Let's Encrypt's rate limit for failed validations.
Once the authoritative name servers answer with the new IP, set
`SITE_ADDRESS=<domain>`, remove the IP from `ALLOWED_HOSTS` and recreate the
containers (see "Changing `.env`"). Caddy obtains the certificate within
seconds.

The GHCR image must be pullable: make the package public (GitHub → package
settings → visibility) or `docker login ghcr.io` on the server with a
read-only token.

Then:

```bash
scripts/deploy.sh
docker compose -f compose.prod.yaml exec web python manage.py createsuperuser
```

Check `https://<domain>/`, log in to `/admin/`. Test email sending:

```bash
docker compose -f compose.prod.yaml exec -T web python manage.py sendtestemail <address>
```

### Changing `.env`

`docker compose up -d` does not notice changes inside `.env`. Recreate the
affected containers:

```bash
docker compose -f compose.prod.yaml up -d --force-recreate web    # Django settings
docker compose -f compose.prod.yaml up -d --force-recreate caddy  # SITE_ADDRESS, ROBOTS_TAG
```

## 4. Deploying updates

After a PR is merged, CI pushes a new image (`latest` and `sha-<commit>`).
Wait until the CI run for the merge commit has pushed it
(`gh run list --branch main --limit 1`), otherwise `latest` is still the
previous build. Then:

```bash
ssh {{SSH_TARGET}} 'cd /srv/{{PROJECT_SLUG}} && scripts/deploy.sh'
curl -s {{LIVE_URL}}/version   # {"commit": "<sha>", "short": "<sha7>"}
```

The script pulls the repo and images, runs migrations, restarts the
containers and removes old images. The commit is baked into the image by CI
(`GIT_COMMIT` build arg → `APP_COMMIT`); locally built images report `dev`.

**Rollback** to an earlier build: set `IMAGE_TAG=sha-<commit>` in `.env` and
run `scripts/deploy.sh` again (set it back to `latest` afterwards). Migrations
are not rolled back automatically.

## 5. Scheduled jobs

`crontab -e` as `deploy`:

```cron
# Database dump before the UpCloud backup, nightly 02:00
0 2 * * * cd /srv/{{PROJECT_SLUG}} && scripts/backup-db.sh
```

Add project-specific jobs (e.g. deleting old form submissions) here and in
`docs/STATUS.md`. After changing the time zone, `systemctl restart cron`.
Schedule the UpCloud backup after the dump (ADR 0008).

## 6. Backups and restore

- `scripts/backup-db.sh` writes `backups/db-YYYY-MM-DD.dump`
  (`pg_dump` custom format) and keeps 14 days (`KEEP_DAYS`).
- Uploaded files live in the Docker volume `<project>_media`; the UpCloud
  backup of the disk covers them.

Restore a dump into the running database:

```bash
docker compose -f compose.prod.yaml exec -T db \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' \
  < backups/db-YYYY-MM-DD.dump
```

## 7. Logs and status

```bash
docker compose -f compose.prod.yaml ps
docker compose -f compose.prod.yaml logs --tail 100 web    # Django/Gunicorn
docker compose -f compose.prod.yaml logs --tail 100 caddy  # access log, TLS
```

## 8. Go-live

1. DNS: point the main domain (and e.g. `www`) to the server; remove old
   `AAAA` records that point elsewhere. Do not touch mail records. If the
   domain is attached to an old web hosting, detach it there first, otherwise
   the provider may reset the records.
2. Wait until the authoritative name servers answer with the new IP (`dig`,
   see section 2).
3. Update `.env` and deploy:

   ```
   SITE_ADDRESS=<domain>
   REDIRECT_ADDRESSES=www.<domain>
   ALLOWED_HOSTS=<domain>
   CSRF_TRUSTED_ORIGINS=https://<domain>
   ROBOTS_TAG=all
   ```

   ```bash
   scripts/deploy.sh   # recreates web and caddy with the new .env
   ```

4. Check: `https://<domain>/` (200, no `X-Robots-Tag: noindex`), redirects
   (301 to the main address), admin login, forms and email.
5. Record the go-live in `docs/STATUS.md`. Caddy sends HSTS for one year
   (without subdomains) – from now on the domain must stay on HTTPS.
