# 0004: Python tooling: uv and Ruff

- Status: accepted
- Date: YYYY-MM-DD

## Context

Dependencies should be reproducible and the tooling lean and fast.

## Decision

- **uv** manages the Python version, virtual environment and dependencies
  (`pyproject.toml` + `uv.lock`, both committed). Also used in the Docker image.
- **Ruff** handles linting and formatting (instead of flake8/isort/black),
  configured in `pyproject.toml`. Runs in CI and before every commit.

## Consequences

- One lockfile, identical versions locally, in CI and on the server.
- No `requirements.txt`, no `pip install`.
