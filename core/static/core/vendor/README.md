# Vendored third-party files

Served from our own origin (ADR 0011, 0013). Never edit by hand; replace
the whole directory when upgrading, and pin versions that are at least two
weeks old. The only change made: `//# sourceMappingURL=` comments removed
(the `.map` files are not vendored, and Django's manifest storage would
fail on the missing files).

| Directory | Package | Files | Licence |
|---|---|---|---|
| `maplibre-gl-6.16.0/` | npm `maplibre-gl` 6.16.0 | `dist/maplibre-gl.mjs`, `dist/maplibre-gl-worker.mjs`, `dist/maplibre-gl.css` | BSD-3-Clause (`LICENSE.txt`) |
| `pmtiles-4.5.0/` | npm `pmtiles` 4.5.0 | `dist/pmtiles.js` | BSD-3-Clause (`LICENSE.txt`) |
