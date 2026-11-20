# 0011: Interactivity with plain JavaScript modules and htmx

- Status: accepted
- Date: 2026-11-20

## Context

Rooterium should feel "beautiful and interactive" (map, filters, cards,
toggles), more than the typical template site. ADR 0002 already says to try
small tools like htmx before a JS framework. This ADR makes it binding for
Rooterium.

## Decision

- Pages are rendered by Django/Wagtail templates. Interactivity is added with
  **plain JavaScript ES modules** (`<script type="module">`) and, where it
  helps (partial page updates such as filtering lists, form submissions),
  **htmx**.
- **No React/Vue/SPA and no frontend build step** (no npm, bundler or
  transpiler). Third-party JS (htmx, MapLibre) is vendored into static files
  at an exact version, never loaded from a CDN (ADR 0013).
- Progressive enhancement: content and links work without JavaScript; the
  map has a list fallback.
- Introducing a framework or a build step requires a new ADR.

## Consequences

- Simple to run and hand over: no Node toolchain, static files are collected
  as usual.
- Larger interactive pieces (the map) need careful hand-written modules and
  tests in the browser; there is no component framework to lean on.
