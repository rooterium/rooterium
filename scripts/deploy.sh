#!/bin/sh
# Deploy the latest image on the production server (run from the repo
# checkout, e.g. /srv/<project>). Optional: IMAGE_TAG=sha-<commit> to pin a build.
set -eu
cd "$(dirname "$0")/.."

compose() { docker compose -f compose.prod.yaml "$@"; }

git pull --ff-only
compose pull web caddy
compose up -d db
# Migrations run once, before the new version takes traffic.
compose run --rm web python manage.py migrate --noinput
compose up -d --remove-orphans
docker image prune -f
compose ps
