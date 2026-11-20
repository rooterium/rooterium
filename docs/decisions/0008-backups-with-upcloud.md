# 0008: Backups with UpCloud's backup service

- Status: accepted
- Date: YYYY-MM-DD

## Context

The server holds the PostgreSQL database, uploaded media and the production
`.env`. Backups should require as little custom tooling as possible.

## Decision

Use UpCloud's built-in server backups (scheduled storage snapshots).

To make the database restorable reliably, a nightly cron job writes a
`pg_dump` to a directory on the server's disk shortly before the snapshot
runs. The snapshot then contains a consistent dump in addition to the raw
PostgreSQL volume.

## Consequences

- No extra backup target, account or script beyond the dump job.
- Restore = restore the snapshot (whole server) or extract the dump from it.
- Backups stay with the same provider; acceptable for this site's size and
  risk profile. Revisit if an off-provider copy becomes a requirement.
- Backup schedule and retention are configured in the UpCloud control panel
  and documented in `docs/architecture.md`.
