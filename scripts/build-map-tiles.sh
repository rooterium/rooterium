#!/usr/bin/env bash
# Build the map tiles for the home page: PMTiles extracts of historic
# Armenia and the South Caucasus –
#   - vector tiles from the Protomaps daily build (ADR 0015) -> OUTPUT,
#   - terrain (elevation) from Mapterhorn for the relief (ADR 0016) ->
#     terrain.pmtiles next to OUTPUT.
#
# Usage: scripts/build-map-tiles.sh [OUTPUT] [BUILD]
#   OUTPUT  default: media/maps/rooterium.pmtiles (local development)
#   BUILD   Protomaps build date (YYYYMMDD), default: latest
#
# Downloads the pinned go-pmtiles CLI from GitHub, verifies its SHA-256 and
# runs `pmtiles extract` (only the needed byte ranges are downloaded).
set -euo pipefail

VERSION=1.31.2
BBOX=36.5,36.0,50.5,43.6
MAXZOOM=10
# Relief: zoom 8 is enough for the shading (MapLibre over-zooms), ~25 MB.
TERRAIN_SOURCE=https://download.mapterhorn.com/planet.pmtiles
TERRAIN_MAXZOOM=8
OUTPUT=${1:-media/maps/rooterium.pmtiles}
BUILD=${2:-}

case "$(uname -s)_$(uname -m)" in
  Darwin_arm64)  ASSET=go-pmtiles-${VERSION}_Darwin_arm64.zip
                 SHA=40528f7f616fcbf91207cd48c8fc023d213f6d86c0cbf1f748732803d1880f3d ;;
  Darwin_x86_64) ASSET=go-pmtiles-${VERSION}_Darwin_x86_64.zip
                 SHA=1f0dc02eee6c58312dd6c509faee1b5c32f0596568af1bf51f1b034e7a88a65b ;;
  Linux_x86_64)  ASSET=go-pmtiles_${VERSION}_Linux_x86_64.tar.gz
                 SHA=3ed7dbf4ec2e6dfe5e25b6f70d1ffc932729f93c86db353bf514dd71010a312f ;;
  Linux_aarch64|Linux_arm64)
                 ASSET=go-pmtiles_${VERSION}_Linux_arm64.tar.gz
                 SHA=f8bd47e7ea866863489cad588fbaf2f31f42e5821f7a03f009b3769f05801cb1 ;;
  *) echo "Unsupported platform: $(uname -s) $(uname -m)" >&2; exit 1 ;;
esac

if [ -z "$BUILD" ]; then
  BUILD=$(curl -fsSL https://build-metadata.protomaps.dev/builds.json \
    | python3 -c 'import json, sys; print(json.load(sys.stdin)[-1]["key"].removesuffix(".pmtiles"))')
fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "Downloading go-pmtiles ${VERSION} (${ASSET})"
curl -fsSL -o "$WORK/$ASSET" \
  "https://github.com/protomaps/go-pmtiles/releases/download/v${VERSION}/${ASSET}"
echo "${SHA}  $WORK/$ASSET" | shasum -a 256 -c -
case "$ASSET" in
  *.zip) unzip -q "$WORK/$ASSET" -d "$WORK" ;;
  *) tar -xzf "$WORK/$ASSET" -C "$WORK" ;;
esac

mkdir -p "$(dirname "$OUTPUT")"
echo "Extracting build ${BUILD}: bbox ${BBOX}, max zoom ${MAXZOOM} -> ${OUTPUT}"
"$WORK/pmtiles" extract "https://build.protomaps.com/${BUILD}.pmtiles" "$OUTPUT.tmp" \
  --bbox="$BBOX" --maxzoom="$MAXZOOM"
mv "$OUTPUT.tmp" "$OUTPUT"

TERRAIN="$(dirname "$OUTPUT")/terrain.pmtiles"
echo "Extracting terrain: bbox ${BBOX}, max zoom ${TERRAIN_MAXZOOM} -> ${TERRAIN}"
"$WORK/pmtiles" extract "$TERRAIN_SOURCE" "$TERRAIN.tmp" \
  --bbox="$BBOX" --maxzoom="$TERRAIN_MAXZOOM"
mv "$TERRAIN.tmp" "$TERRAIN"
ls -lh "$OUTPUT" "$TERRAIN"
