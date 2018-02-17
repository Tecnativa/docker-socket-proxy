FROM haproxy:1.7-alpine
LABEL maintainer="Tecnativa <info@tecnativa.com>"

EXPOSE 2375
VOLUME /run/docker-filtered
ENV AUTH=0 \
    BUILD=0 \
    COMMIT=0 \
    CONTAINERS=0 \
    EVENTS=1 \
    EXEC=0 \
    IMAGES=0 \
    INFO=0 \
    NETWORKS=0 \
    NODES=0 \
    PING=1 \
    PLUGINS=0 \
    POST=0 \
    SECRETS=0 \
    SERVICES=0 \
    SWARM=0 \
    SYSTEM=0 \
    TASKS=0 \
    VERSION=1 \
    VOLUMES=0 \
    SOCK_NETWORK=1 \
    SOCK_DISK=1
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

# Metadata
ARG VCS_REF
ARG BUILD_DATE
LABEL org.label-schema.schema-version="1.1" \
      org.label-schema.vendor=Tecnativa \
      org.label-schema.license=Apache-2.0 \
      org.label-schema.build-date="$BUILD_DATE" \
      org.label-schema.vcs-ref="$VCS_REF" \
      org.label-schema.vcs-url="https://github.com/Tecnativa/docker-tcp-proxy"

