# =============================================================================
# Build Arguments (global)
# =============================================================================
ARG NPM_REGISTRY=https://registry.npmjs.org
ARG STRICT_SSL=true
ARG BASE_IMAGE=docker.io/ubuntu:noble

# =============================================================================
# Stage 1: BUILD — npm install + bundle vendor frontend assets
# =============================================================================
FROM docker.io/node:20-slim AS frontend

ARG NPM_REGISTRY
ARG STRICT_SSL

WORKDIR /build

RUN mkdir -p dist

COPY package*.json ./
COPY scripts/ ./scripts
RUN npm config set registry ${NPM_REGISTRY} \
    && npm config set strict-ssl ${STRICT_SSL} \
    && npm install && bash scripts/copy-assets.sh

# =============================================================================
# Stage 2: RUN — Python application served by uWSGI
# =============================================================================
FROM ${BASE_IMAGE}

# Install system dependencies
RUN apt-get update \
    && apt-get --no-install-recommends install -y \
      dumb-init gcc python3-dev python3-pip python3-venv \
      uwsgi-core uwsgi-plugin-python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lufa

# User context
RUN useradd -ms /bin/bash lufa \
    && chown root:lufa .

# Install Python dependencies
COPY --chown=root:lufa --chmod=755 requirements.txt ./
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=root:lufa --chmod=755 lufa ./lufa
COPY --chown=root:lufa --chmod=755 lufa.ini wsgi.py pyproject.toml ./
COPY --from=frontend --chown=root:lufa --chmod=755 /build/lufa/static/dist ./lufa/static/dist

USER lufa

# run
EXPOSE 8080/tcp

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/opt/venv/bin/uwsgi", "lufa.ini"]

