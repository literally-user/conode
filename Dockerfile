FROM python:3.13-slim-bookworm AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_PATH=/prodik \
    UV_VERSION=0.9.22

ENV VIRTUAL_ENV="$APP_PATH/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR $APP_PATH


FROM python-base AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc git \
    && rm -rf /var/lib/apt/lists/

RUN pip install "uv==$UV_VERSION"
COPY pyproject.toml config.toml ./
RUN uv venv -p 3.13
RUN uv sync --all-extras
COPY src ./src
RUN uv pip install -e .


FROM python-base AS runner

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY --from=builder $APP_PATH/src $APP_PATH/src
COPY --from=builder $APP_PATH/pyproject.toml $APP_PATH/pyproject.toml
COPY --from=builder $APP_PATH/config.toml $APP_PATH/config.toml