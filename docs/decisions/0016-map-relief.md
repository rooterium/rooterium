# 0016: Relief on the home page map

- Status: accepted
- Date: 2026-11-20

## Context

The agreed design, variant B (`design/mockup-2b-map.png`), shows the home
page map as a warm, glowing relief: rust lowlands, orange highlands, pale
peaks. The mockup draws it on an AI-generated mood image with
illustrative positions; the real map must use exact coordinates (brief,
section 6). The map from ADR 0015 (land, water, land cover only) looked
flat and did not match the design.

## Decision

1. **Terrain data: a Mapterhorn PMTiles extract**, self-hosted like the
   vector tiles (ADR 0015, ADR 0013: no third-party requests).
   - Source: `https://download.mapterhorn.com/planet.pmtiles` (Terrarium
     encoded elevation, 512 px WebP tiles). For this region the data comes
     from the Copernicus DEM GLO-30, which is free to use with attribution.
   - Same bounding box as the vector tiles, **max zoom 8** (about 25 MB;
     MapLibre over-zooms for closer views).
   - Built by `scripts/build-map-tiles.sh` into
     `MEDIA_ROOT/maps/terrain.pmtiles`, next to the vector tiles; not in
     git, not in the image.
2. **Style:** a `color-relief` layer (colour by elevation, from dark rust
   to parchment for the highest peaks) and a multidirectional `hillshade`
   layer, both from the terrain file, between land and water in the style
   in `core/static/core/js/map.js`. The land cover layer is only used when
   the terrain file is missing.
3. **Markers as in the mockup:** glowing dot, name in a dark pill, shown
   from the start view; labels that would overlap another are hidden
   (they appear on hover, focus and selection). The selected marker is
   larger with a pomegranate ring.
4. **Attribution** in the map's attribution control: "© Mapterhorn,
   Copernicus DEM GLO-30 © DLR e.V. 2010–2014 and © Airbus Defence and
   Space GmbH 2014–2018, provided under COPERNICUS by the European Union
   and ESA". On narrow maps the credits start collapsed behind the "i"
   button.

## Consequences

- The map now matches the design without invented geography.
- One more file in the media volume (and its backups); each environment
  runs the build script once.
- Without the terrain file the map falls back to the flat ADR 0015 style.
- Mapterhorn's own pages do not state a licence for the derived tiles;
  the upstream licence (Copernicus) is the relevant one. Re-check
  `https://mapterhorn.com/attribution` when rebuilding.
