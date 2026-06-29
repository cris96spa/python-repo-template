ARG PYTHON_VERSION=3.12

# --- Base Stage --- #
FROM python:${PYTHON_VERSION}-slim AS base
ARG UID=10000
ARG GID=10000
ARG PROJECT_NAME=python_repo_template
ARG USER=app
ARG WORKDIR=/app

ENV UV_CACHE_DIR=$WORKDIR/.uv_cache \
    UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UID=$UID \
    GID=$GID \
    PROJECT_NAME=$PROJECT_NAME \
    PATH="$WORKDIR/.venv/bin:/usr/local/bin:$PATH"

RUN groupadd --system --gid $GID $USER \
    && useradd --system --uid $UID --gid $GID -m -d /home/$USER $USER \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh

WORKDIR $WORKDIR

# --- Builder Stage --- #
FROM base AS builder

RUN --mount=type=secret,id=netrc,target=/root/.netrc,uid=0,gid=0,mode=0600 \
    --mount=type=cache,target=$UV_CACHE_DIR,uid=$UID,gid=$GID \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=LICENSE,target=LICENSE \
    uv sync --locked --no-install-project --no-dev

COPY --chown=$USER:$USER uv.lock pyproject.toml README.md LICENSE ./

RUN --mount=type=secret,id=netrc,target=/root/.netrc,uid=0,gid=0,mode=0600 \
    --mount=type=cache,target=$UV_CACHE_DIR,uid=$UID,gid=$GID \
    uv sync --locked --no-dev

# --- Runtime Stage --- #
FROM base AS runtime
COPY --from=builder --chown=$USER:$USER $WORKDIR $WORKDIR

COPY --chown=$USER:$USER $PROJECT_NAME ./$PROJECT_NAME
COPY --chown=$USER:$USER main.py ./main.py

USER $USER
CMD ["python", "main.py", "--number", "10"]
