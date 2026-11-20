#!/bin/sh
# Nightly database dump before the UpCloud backup (ADR 0008). Run by cron on
# the production server. Keeps the last KEEP_DAYS days in ./backups.
set -eu
cd "$(dirname "$0")/.."

KEEP_DAYS="${KEEP_DAYS:-14}"
mkdir -p backups
file="backups/db-$(date +%Y-%m-%d).dump"

# Custom format: compressed, restorable with pg_restore.
docker compose -f compose.prod.yaml exec -T db \
    sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
    > "$file.tmp"
mv "$file.tmp" "$file"
chmod 600 "$file"

find backups -name 'db-*.dump' -mtime +"$KEEP_DAYS" -delete
