// Home page map (ADR 0010, 0015): MapLibre with self-hosted PMTiles,
// HTML button markers, theme filters, side card, homeland/diaspora toggle.
// Progressive enhancement: the place list in the page works without it.

const section = document.querySelector("[data-map]");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

// Initial view: historic Armenia and the South Caucasus.
const CENTER = [44.2, 40.0];
const ZOOM = 5.6;
const LABEL_ZOOM = 8;
const BOUNDS = [
  [33.0, 33.5],
  [54.0, 46.5],
];

function token(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Our own minimal style from the CSS tokens: land, water, land cover.
// No labels (no glyph files needed), no roads, no political borders.
function buildStyle(tilesUrl) {
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
    url: `pmtiles://${new URL(tilesUrl, window.location.href).href}`,
    attribution:
      '<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, ' +
      '<a href="https://protomaps.com">Protomaps</a>',
  };
  const gold = token("--gold");
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
    // Earth tones per land cover kind (Protomaps basemap v4).
    {
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
    },
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

  const state = {
    setFilter(filter) {
      markers.forEach(({ feature, element }) => {
        element.hidden = !(filter === "all" || feature.category === filter);
      });
      filterPlaceList(filter);
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
      return;
    }
    entry.element.setAttribute("aria-pressed", "true");
    card.showFeature(entry.feature);
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
  if (tilesUrl && window.pmtiles) {
    const protocol = new window.pmtiles.Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
  }

  try {
    map = new maplibregl.Map({
      container: section.querySelector("[data-map-canvas]"),
      style: buildStyle(tilesUrl && window.pmtiles ? tilesUrl : ""),
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
  const canvas = section.querySelector("[data-map-canvas]");
  const updateLabels = () => canvas.classList.toggle("show-labels", map.getZoom() >= LABEL_ZOOM);
  map.on("zoom", updateLabels);
  updateLabels();

  section.classList.add("has-map");
}

if (section) {
  init();
}
