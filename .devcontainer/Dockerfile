ARG BASE_IMAGE=docker.io/ubuntu:noble
FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y && apt install -y python3 python3-pip git npm

WORKDIR /workspace

COPY ../requirements.txt ../requirements-dev.txt /workspace/

COPY package*.json /workspace
COPY scripts/ /workspace/scripts
RUN npm config set registry ${NPM_REGISTRY} \
    && npm config set strict-ssl ${STRICT_SSL} \
    && npm install && bash scripts/copy-assets.sh \
    && pip3 install --break-system-packages -r /workspace/requirements.txt \
    -r /workspace/requirements-dev.txt && rm -f /workspace/requirements.txt \
    /workspace/requirements-dev.txt
