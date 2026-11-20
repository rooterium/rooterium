# 0006: Build images in GitHub Actions

- Status: accepted
- Date: YYYY-MM-DD

## Context

Development happens on Apple Silicon (arm64), the server is x86_64. Building
amd64 images locally (emulation) is slow and error-prone; building on the
server puts load on it and requires the source code there.

## Decision

GitHub Actions builds the production image for `linux/amd64` and pushes it to
the **GitHub Container Registry (ghcr.io)**. Ruff and the tests run before the
build. The server only pulls finished images (`docker compose pull`).

## Consequences

- Reproducible images; the server needs no build toolchain.
- Images are tagged with the commit SHA → easy rollback.
- The server needs read access to GHCR (token or public image).
- Locally, images are still built natively for arm64.
