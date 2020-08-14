ARG REPO=library
FROM ${REPO}/haproxy:lts-alpine

EXPOSE 2375
ENV ALLOW_RESTARTS=0 \
    AUTH=0 \
    BUILD=0 \
    COMMIT=0 \
    CONFIGS=0 \
    CONTAINERS=0 \
    DISTRIBUTION=0 \
    EVENTS=1 \
    EXEC=0 \
    IMAGES=0 \
    INFO=0 \
    LOG_LEVEL=info \
    NETWORKS=0 \
    NODES=0 \
    PING=1 \
    PLUGINS=0 \
    POST=0 \
    DELETE=0 \
    SECRETS=0 \
    SERVICES=0 \
    SESSION=0 \
    SWARM=0 \
    SYSTEM=0 \
    TASKS=0 \
    VERSION=1 \
    VOLUMES=0 \
    CONTAINERS_CREATE=0 \
    CONTAINERS_PRUNE=0 \
    CONTAINERS_RESIZE=0 \
    CONTAINERS_START=0 \
    CONTAINERS_UPDATE=0 \
    CONTAINERS_RENAME=0 \
    CONTAINERS_PAUSE=0 \
    CONTAINERS_UNPAUSE=0 \
    CONTAINERS_ATTACH=0 \
    CONTAINERS_WAIT=0 \
    CONTAINERS_EXEC=0 \
    VOLUMES_CREATE=0 \
    VOLUMES_PRUNE=0 \
    NETWORKS_CREATE=0 \
    NETWORKS_PRUNE=0 \
    NETWORKS_CONNECT=0 \
    NETWORKS_DISCONNECT=0 \
    NETWORKS_DELETE=0 \
    CONTAINERS_DELETE=0 \
    IMAGES_DELETE=0 \
    VOLUMES_DELETE=0
    
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

# Metadata
ARG VCS_REF
ARG BUILD_DATE
LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.vendor=Tecnativa \
      org.label-schema.license=Apache-2.0 \
      org.label-schema.build-date="$BUILD_DATE" \
      org.label-schema.vcs-ref="$VCS_REF" \
      org.label-schema.vcs-url="https://github.com/Tecnativa/docker-socket-proxy"
