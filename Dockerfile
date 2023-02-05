FROM haproxy:2.7-alpine
USER root

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY start.sh /usr/local/bin/start.sh

RUN apk upgrade --no-cache && \
    apk add --no-cache ca-certificates wget tzdata openssl && \
    chmod +x /usr/local/bin/start.sh

ENV ALLOW_RESTARTS=0 \
    AUTH=0 \
    BUILD=0 \
    COMMIT=0 \
    CONFIGS=0 \
    CONTAINERS=0 \
    DISTRIBUTION=0 \
    EVENTS=1 \
    EXEC=0 \
    GRPC=0 \
    IMAGES=0 \
    INFO=0 \
    LOG_LEVEL=info \
    NETWORKS=0 \
    NODES=0 \
    PING=1 \
    PLUGINS=0 \
    POST=0 \
    SECRETS=0 \
    SERVICES=0 \
    SESSION=0 \
    SOCKET_PATH=/var/run/docker.sock \
    SWARM=0 \
    SYSTEM=0 \
    TASKS=0 \
    VERSION=1 \
    VOLUMES=0
    
ENTRYPOINT start.sh