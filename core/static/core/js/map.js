// Home page map (ADR 0010, 0015): MapLibre with self-hosted PMTiles,
// HTML button markers, theme filters, side card, homeland/diaspora toggle.
// Progressive enhancement: the place list in the page works without it.

const section = document.querySelector("[data-map]");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

// Initial view: historic Armenia and the South Caucasus.
const CENTER = [44.2, 40.0];
const ZOOM = 5.6;
// Names next to all markers from this zoom on (the start view shows them,
// as in the mockup); below, on hover, focus or selection only.
const LABEL_ZOOM = 5;
const BOUNDS = [
  [33.0, 33.5],
  [54.0, 46.5],
];

function token(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Elevation colours (metres) for the relief (ADR 0016), after the variant B
// mockup: dark rust lowlands, glowing orange highlands, parchment peaks.
const RELIEF = [
  -100, "#24130c",
  0, "#2a150d",
  500, "#3f1d10",
  1000, "#5e2812",
  1500, "#813814",
  2000, "#9c4c1b",
  2500, "#b0652f",
  3000, "#bf8452",
  3800, "#d3b089",
  4600, "#e6d3b8",
  5200, "#eee3d1",
];

const TERRAIN_ATTRIBUTION =
  '<a href="https://mapterhorn.com/attribution">© Mapterhorn</a>, ' +
  "Copernicus DEM GLO-30 © DLR e.V. 2010–2014 and © Airbus Defence and " +
  "Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA";

function pmtilesUrl(path) {
  return `pmtiles://${new URL(path, window.location.href).href}`;
}

// Elevation colours plus hill shading from the terrain file, if present.
function reliefLayers(style, terrainUrl) {
  if (!terrainUrl) {
    return [];
  }
  style.sources.terrain = {
    type: "raster-dem",
    url: pmtilesUrl(terrainUrl),
    encoding: "terrarium",
    tileSize: 512,
    attribution: TERRAIN_ATTRIBUTION,
  };
  return [
    {
      id: "relief-colour",
      type: "color-relief",
      source: "terrain",
      paint: {
        "color-relief-color": [
          "interpolate",
          ["linear"],
          ["elevation"],
          ...RELIEF,
        ],
      },
    },
    {
      id: "hillshade",
      type: "hillshade",
      source: "terrain",
      paint: {
        "hillshade-method": "multidirectional",
        "hillshade-exaggeration": 0.55,
        "hillshade-shadow-color": "rgba(11, 10, 9, 0.85)",
        "hillshade-highlight-color": "rgba(240, 200, 140, 0.45)",
        "hillshade-accent-color": "rgba(60, 20, 8, 0.6)",
      },
    },
  ];
}

// Our own minimal style from the CSS tokens: land, relief, water.
// No labels (no glyph files needed), no roads, no political borders.
function buildStyle(tilesUrl, terrainUrl) {
  const bg = token("--bg");
  const style = {
    version: 8,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": bg } }],
  };
  if (!tilesUrl) {
    return style;
  }
  style.sources.protomaps = {
    type: "vector",
    url: pmtilesUrl(tilesUrl),
    attribution:
      '<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, ' +
      '<a href="https://protomaps.com">Protomaps</a>',
  };
  const gold = token("--gold");
  const relief = reliefLayers(style, terrainUrl);
  style.layers = [
    // Outside land (the sea) uses the page background.
    { id: "background", type: "background", paint: { "background-color": bg } },
    {
      id: "earth",
      type: "fill",
      source: "protomaps",
      "source-layer": "earth",
      paint: { "fill-color": "#261d16" },
    },
    ...relief,
    // Earth tones per land cover kind (Protomaps basemap v4); only without
    // the relief, which would be hidden by it.
    ...(relief.length ? [] : [{
      id: "landcover",
      type: "fill",
      source: "protomaps",
      "source-layer": "landcover",
      paint: {
        "fill-color": [
          "match",
          ["get", "kind"],
          "barren",
          "#3a2b1e",
          "scrub",
          "#30241a",
          "grassland",
          "#2d2219",
          "forest",
          "#222016",
          "farmland",
          "#2a1f17",
          "glacier",
          "#9a9184",
          "urban_area",
          "#33281f",
          "#261d16",
        ],
        "fill-opacity": ["match", ["get", "kind"], "glacier", 0.55, 0.85],
      },
    }]),
    {
      id: "water",
      type: "fill",
      source: "protomaps",
      "source-layer": "water",
      filter: ["==", ["geometry-type"], "Polygon"],
      paint: { "fill-color": "#0a0d0f" },
    },
    // Fine gold coastlines and lake shores.
    {
      id: "shoreline",
      type: "line",
      source: "protomaps",
      "source-layer": "water",
      filter: ["==", ["geometry-type"], "Polygon"],
      paint: {
        "line-color": gold,
        "line-opacity": ["interpolate", ["linear"], ["zoom"], 4, 0.5, 9, 0.7],
        "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.6, 9, 1.2],
      },
    },
    {
      id: "rivers",
      type: "line",
      source: "protomaps",
      "source-layer": "water",
      filter: [
        "all",
        ["==", ["geometry-type"], "LineString"],
        ["in", ["get", "kind"], ["literal", ["river", "canal"]]],
      ],
      paint: {
        "line-color": "#3d5560",
        "line-width": ["interpolate", ["linear"], ["zoom"], 5, 0.8, 10, 2.2],
      },
    },
  ];
  return style;
}

function initControls(state) {
  const chips = [...section.querySelectorAll("[data-filter]")];
  const views = [...section.querySelectorAll("[data-view]")];
  const diaspora = section.querySelector("[data-diaspora]");

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      state.setFilter(chip.dataset.filter);
    });
  });

  views.forEach((button) => {
    button.addEventListener("click", () => {
      views.forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
      const isDiaspora = button.dataset.view === "diaspora";
      diaspora.hidden = !isDiaspora;
      section.classList.toggle("is-diaspora", isDiaspora);
      // Markers behind the "coming later" overlay must not be focusable.
      section.querySelector("[data-map-canvas]").inert = isDiaspora;
    });
  });
}

function createCard() {
  const card = section.querySelector("[data-card]");
  const parts = {
    default: card.querySelector("[data-card-default]"),
    feature: card.querySelector("[data-card-feature]"),
    category: card.querySelector("[data-card-category]"),
    title: card.querySelector("[data-card-title]"),
    description: card.querySelector("[data-card-description]"),
    link: card.querySelector("[data-card-link]"),
    panels: [...card.querySelectorAll("[data-card-panel]")],
  };

  function show(which) {
    parts.default.hidden = which !== "default";
    parts.feature.hidden = which !== "feature";
    parts.panels.forEach((panel) => {
      panel.hidden = panel.dataset.cardPanel !== which;
    });
  }

  return {
    showDefault: () => show("default"),
    showPanel: (name) => show(name),
    showFeature(feature) {
      parts.category.textContent = feature.categoryLabel;
      parts.title.textContent = feature.name;
      parts.description.textContent = feature.description;
      parts.link.hidden = !feature.url;
      if (feature.url) {
        parts.link.href = feature.url;
        parts.link.textContent = `${feature.linkLabel} →`;
      }
      show("feature");
    },
  };
}

function filterPlaceList(filter) {
  section.querySelectorAll("[data-place-item]").forEach((item) => {
    item.hidden = !(filter === "all" || item.dataset.category === filter);
  });
}

async function init() {
  const features = JSON.parse(document.getElementById("map-features").textContent);
  const card = createCard();
  const markers = [];
  let selected = null;
  let map = null;
  let labelsChanged = () => {};

  const state = {
    setFilter(filter) {
      markers.forEach(({ feature, element }) => {
        element.hidden = !(filter === "all" || feature.category === filter);
      });
      filterPlaceList(filter);
      labelsChanged();
      if (selected && selected.element.hidden) {
        select(null);
      }
      if (filter === "events" || filter === "projects") {
        card.showPanel(filter);
      } else if (!selected) {
        card.showDefault();
      }
    },
  };
  initControls(state);

  function select(entry) {
    if (selected) {
      selected.element.setAttribute("aria-pressed", "false");
    }
    selected = entry;
    if (!entry) {
      card.showDefault();
      labelsChanged();
      return;
    }
    entry.element.setAttribute("aria-pressed", "true");
    card.showFeature(entry.feature);
    labelsChanged();
    const target = { center: [entry.feature.lng, entry.feature.lat] };
    if (reducedMotion.matches) {
      map.jumpTo(target);
    } else {
      map.easeTo({ ...target, duration: 600 });
    }
  }

  let maplibregl;
  try {
    maplibregl = await import(section.dataset.maplibre);
  } catch (error) {
    console.error("Map could not be loaded", error);
    section.querySelector(".place-list").open = true;
    return;
  }

  const tilesUrl = section.dataset.tiles;
  maplibregl.setWorkerUrl(section.dataset.worker);
  if ((tilesUrl || section.dataset.terrain) && window.pmtiles) {
    const protocol = new window.pmtiles.Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
  }

  try {
    map = new maplibregl.Map({
      container: section.querySelector("[data-map-canvas]"),
      style: buildStyle(
        tilesUrl && window.pmtiles ? tilesUrl : "",
        section.dataset.terrain && window.pmtiles ? section.dataset.terrain : "",
      ),
      center: CENTER,
      zoom: ZOOM,
      minZoom: 4,
      maxZoom: 13,
      maxBounds: BOUNDS,
      dragRotate: false,
      pitchWithRotate: false,
      touchPitch: false,
      cooperativeGestures: true,
      attributionControl: { compact: true },
    });
  } catch (error) {
    // No WebGL: keep the list.
    console.error("Map could not be created", error);
    section.querySelector(".place-list").open = true;
    return;
  }
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  // On small maps the credits (OSM, Protomaps, Mapterhorn, Copernicus) start
  // collapsed behind the "i" button instead of covering the map.
  if (section.querySelector("[data-map-canvas]").clientWidth < 600) {
    map.once("load", () => {
      section.querySelector(".maplibregl-ctrl-attrib")?.classList.remove("maplibregl-compact-show");
    });
  }
  map.touchZoomRotate.disableRotation();

  features.forEach((feature) => {
    const element = document.createElement("button");
    element.type = "button";
    element.className = `map-marker map-marker--${feature.category === "events" ? "event" : "place"}`;
    element.setAttribute("aria-pressed", "false");
    element.setAttribute("aria-label", `${feature.name} (${feature.categoryLabel})`);
    const label = document.createElement("span");
    label.className = "map-marker-label";
    label.textContent = feature.name;
    label.setAttribute("aria-hidden", "true");
    element.append(label);
    const entry = { feature, element };
    element.addEventListener("click", (event) => {
      event.stopPropagation();
      select(selected === entry ? null : entry);
    });
    // The dot's centre is 22 px from the button's left edge (CSS).
    new maplibregl.Marker({ element, anchor: "left", offset: [-22, 0] })
      .setLngLat([feature.lng, feature.lat])
      .addTo(map);
    markers.push(entry);
  });

  // Names only when zoomed in; otherwise on hover, focus or selection.
  // Labels that would overlap an earlier one are hidden (selected first).
  const canvas = section.querySelector("[data-map-canvas]");
  const updateLabels = () => {
    canvas.classList.toggle("show-labels", map.getZoom() >= LABEL_ZOOM);
    const taken = [];
    const ordered = selected ? [selected, ...markers.filter((m) => m !== selected)] : markers;
    ordered.forEach(({ element }) => {
      element.classList.remove("label-collides");
      if (element.hidden) {
        return;
      }
      const box = element.querySelector(".map-marker-label").getBoundingClientRect();
      const hit = taken.some(
        (b) => box.left < b.right + 4 && box.right + 4 > b.left && box.top < b.bottom + 2 && box.bottom + 2 > b.top,
      );
      if (hit) {
        element.classList.add("label-collides");
      } else {
        taken.push(box);
      }
    });
  };
  map.on("zoom", () => canvas.classList.toggle("show-labels", map.getZoom() >= LABEL_ZOOM));
  map.on("moveend", updateLabels);
  map.once("idle", updateLabels);
  labelsChanged = updateLabels;
  updateLabels();

  // Deep link from a story: /?place=place-3#explore selects that marker.
  const wanted = new URLSearchParams(window.location.search).get("place");
  const entry = markers.find((m) => m.feature.id === wanted);
  if (entry) {
    map.jumpTo({ center: [entry.feature.lng, entry.feature.lat], zoom: 8 });
    select(entry);
  }

  section.classList.add("has-map");
}

if (section) {
  init();
}
