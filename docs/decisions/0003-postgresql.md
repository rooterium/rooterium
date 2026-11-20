# 0003: PostgreSQL as database

- Status: accepted
- Date: YYYY-MM-DD

## Context

The data volume is small. SQLite would technically suffice, but running in
containers, backups and future extensions favour a real database server.

## Decision

PostgreSQL (current stable major version, official Docker image) in
development **and** production. No SQLite, not even for tests.

## Consequences

- Same behaviour locally and on the server.
- Backups via `pg_dump`.
- One extra container and a volume that must be backed up.
