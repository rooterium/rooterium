# Image for the Django app, used for local development and production.
# Production images are built for linux/amd64 in GitHub Actions (ADR 0006).

FROM python:3.14-slim

# uv binary, pinned to the version used locally.
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Keep the virtualenv outside /app so a bind mount in development does
    # not hide it.
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install dependencies first so this layer is cached until uv.lock changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . .

# Collect static files at build time. Settings require these variables, but
# the values are irrelevant for collectstatic.
RUN SECRET_KEY=build DATABASE_URL=postgres://build@localhost/build \
    python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/media \
    && chown -R app:app /app/media /app/staticfiles
USER app

# Git commit of this build, shown at /version. Set by CI (build arg); local
# builds report "dev". Declared late so it does not invalidate earlier layers.
ARG GIT_COMMIT=dev
ENV APP_COMMIT=${GIT_COMMIT}

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
