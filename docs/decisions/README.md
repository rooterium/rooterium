# Architecture Decision Records

Fundamental decisions, one file each, numbered sequentially.
An ADR is not rewritten after the fact; a changed decision gets a new ADR that
marks the old one as "superseded by".

Template: [`0000-template.md`](0000-template.md). 0001–0008 come from the
project template (`kreuzlin/django-template`); 0009 onwards are Rooterium's
deviations and additions.

| No.  | Title                                                                  | Status   |
|------|------------------------------------------------------------------------|----------|
| 0001 | [Use ADRs](0001-use-adrs.md)                                           | accepted |
| 0002 | [Django with server-side templates](0002-django-with-templates.md)     | accepted, partly superseded by 0009 |
| 0003 | [PostgreSQL as database](0003-postgresql.md)                           | accepted |
| 0004 | [Python tooling: uv and Ruff](0004-uv-and-ruff.md)                     | accepted |
| 0005 | [Hosting: Docker Compose, Caddy, UpCloud](0005-hosting-docker-caddy-upcloud.md) | accepted |
| 0006 | [Build images in GitHub Actions](0006-build-images-in-github-actions.md) | accepted |
| 0007 | [Secrets only in .env](0007-secrets-in-env.md)                         | accepted |
| 0008 | [Backups with UpCloud's backup service](0008-backups-with-upcloud.md) | accepted |
| 0009 | [Wagtail as CMS](0009-wagtail-as-cms.md)                               | accepted |
| 0010 | [Interactive map with MapLibre GL JS](0010-map-with-maplibre.md)       | accepted (tile source: 0015) |
| 0011 | [Interactivity with plain JavaScript modules and htmx](0011-interactivity-without-spa.md) | accepted |
| 0012 | [English first, translatable from day one](0012-english-and-i18n.md)   | accepted |
| 0013 | [Privacy by default](0013-privacy-by-default.md)                       | accepted |
| 0014 | [Content model](0014-content-model.md)                                 | accepted |
| 0015 | [Map tiles and map style](0015-map-tiles-and-style.md)               | accepted (relief: 0016) |
| 0016 | [Relief on the home page map](0016-map-relief.md)                     | accepted |
