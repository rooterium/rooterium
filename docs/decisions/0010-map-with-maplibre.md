# 0010: Interactive map with MapLibre GL JS

- Status: accepted (library); the tile source is decided in milestone 4; the map moves from the home page to `/map/` (ADR 0017)
- Date: 2026-11-20

## Context

The home page is an interactive map of historic Armenia and the South
Caucasus with gold markers, theme filters and a side card (design variant B).
The map must match the dark Rooterium palette, work on phones and with the
keyboard, and must not leak visitors' data to third parties (ADR 0013).

## Decision

- Use **MapLibre GL JS** (open source, BSD licence, vector tiles, fully
  styleable). Its JS and CSS are **self-hosted** from our static files, pinned
  to an exact version; no CDN.
- The map style is our own, in the Rooterium palette (Palette V2 in
  `docs/PROJECT_BRIEF.md`).
- **Tile source:** preference for **self-hosted vector tiles**, e.g. a
  Protomaps PMTiles extract of the region served from our own server (Caddy
  supports HTTP range requests, which PMTiles needs). The final choice
  (extract size, zoom levels, update process, glyphs/fonts for labels,
  attribution) is made in a separate ADR in milestone 4 (issue #4). Until
  then no third-party tile service is used.
- Marker data comes from the places and events in the database, rendered as
  GeoJSON by a Django view.

## Consequences

- No API keys, no usage limits, no tracking by a map provider.
- We are responsible for the tiles: generating the extract, its size on the
  server and in backups, and occasional updates. OpenStreetMap attribution
  must be shown.
- MapLibre is a sizeable script (several hundred kB); it is
  loaded only on pages with a map.
- The map needs a non-map fallback (list of places) for accessibility and for
  browsers without WebGL.
