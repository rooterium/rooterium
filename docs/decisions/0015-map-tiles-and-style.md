# 0015: Map tiles and map style

- Status: accepted
- Date: 2026-11-20

## Context

ADR 0010 chose MapLibre GL JS and left the tile source open, with a
preference for self-hosted vector tiles and no third-party requests from
the visitor's browser (ADR 0013). The home page map (milestone 4, issue #4)
covers historic Armenia and the South Caucasus. The variant B mockups were
not available when this was decided (#13), so the style follows the brief:
dark, warm, "digital atlas", gold markers.

## Decision

1. **Tiles: a Protomaps PMTiles extract of the region**, self-hosted.
   - Source: the Protomaps daily planet build (OpenStreetMap data,
     Protomaps basemap schema v4), extracted with the official
     `go-pmtiles` CLI (pinned version, checksum verified):
     bounding box **36.5° E – 50.5° E, 36.0° N – 43.6° N**, **max zoom 10**
     (MapLibre over-zooms vector tiles beyond that).
   - Script: `scripts/build-map-tiles.sh` writes
     `MEDIA_ROOT/maps/rooterium.pmtiles`. The file is **not in git** (size)
     and not in the image; it lives in the media volume and is rebuilt
     when needed (e.g. once a year).
   - Served at `/media/maps/rooterium.pmtiles` with HTTP range requests:
     by Caddy in production (`file_server` supports ranges), by a small
     DEBUG-only view in development (Django's static `serve` does not).
   - Read in the browser with the `pmtiles` JS library (protocol
     `pmtiles://`), vendored like MapLibre.
2. **Vendored libraries:** MapLibre GL JS **6.16.0** (ES module build; its
   worker is a same-origin module, so the CSP needs no `blob:`) and
   `pmtiles` **4.5.0** (self-contained `pmtiles.js`), in
   `core/static/core/vendor/` with their licences. Versions are at least
   two weeks old when pinned.
3. **Own minimal style**, built in `core/static/core/js/map.js` from the
   CSS tokens: background, land, water (areas and rivers), subtle land
   cover. **No basemap labels** (they would need glyph files; our own
   markers carry the names, in the site fonts) and **no roads**.
4. **No modern political borders** on the map in version 1: the map is
   about historic and cultural places, and borders in the region are
   contested. Whether and how to show borders (modern or historic) is the
   editor's decision later.
5. **Markers are HTML buttons** (gold), keyboard-focusable, with the
   place name as label. Places come from the database (live only), events
   only if they have coordinates. The data is embedded in the page as JSON
   (`json_script`), no separate API.
6. **Fallback:** without JavaScript, WebGL or the tile file, the page shows
   the list of places (always rendered) and, if the tiles are missing, a
   plain background with the markers.
7. **Attribution:** "© OpenStreetMap contributors" and "Protomaps" in the
   map's attribution control (ODbL requirement).

## Consequences

- No third-party requests and no API keys; works offline in development
  once the file exists.
- The tile file (expected tens of MB) must be built on each environment
  and is part of the media volume (and its backups).
- Updating the map data means re-running the script; there is no
  automatic update.
- Running `go-pmtiles` requires downloading a binary from the Protomaps
  GitHub releases; the script verifies its SHA-256.
