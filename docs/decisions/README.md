# Architecture Decision Records

Fundamental decisions, one file each, numbered sequentially.
An ADR is not rewritten after the fact; a changed decision gets a new ADR that
marks the old one as "superseded by".

Template: [`0000-template.md`](0000-template.md). The ADRs below come from
the project template; set their date when creating a project and add
project-specific ones from 0009 on.

| No.  | Title                                                                  | Status   |
|------|------------------------------------------------------------------------|----------|
| 0001 | [Use ADRs](0001-use-adrs.md)                                           | accepted |
| 0002 | [Django with server-side templates](0002-django-with-templates.md)     | accepted |
| 0003 | [PostgreSQL as database](0003-postgresql.md)                           | accepted |
| 0004 | [Python tooling: uv and Ruff](0004-uv-and-ruff.md)                     | accepted |
| 0005 | [Hosting: Docker Compose, Caddy, UpCloud](0005-hosting-docker-caddy-upcloud.md) | accepted |
| 0006 | [Build images in GitHub Actions](0006-build-images-in-github-actions.md) | accepted |
| 0007 | [Secrets only in .env](0007-secrets-in-env.md)                         | accepted |
| 0008 | [Backups with UpCloud's backup service](0008-backups-with-upcloud.md) | accepted |
