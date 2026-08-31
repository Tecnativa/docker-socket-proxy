ARG HAPROXY_VERSION=lts
FROM haproxy:${HAPROXY_VERSION}-alpine

EXPOSE 2375
ENV ALLOW_ARCHIVE=0 \
    ALLOW_ATTACH=0 \
    ALLOW_EXEC=0 \
    ALLOW_EXPORT=0 \
    ALLOW_KILL=0 \
    ALLOW_LOGS=0 \
    ALLOW_PAUSE=0 \
    ALLOW_RESTARTS=0 \
    ALLOW_STOP=0 \
    ALLOW_START=0 \
    ALLOW_UNPAUSE=0 \
    AUTH=0 \
    BUILD=0 \
    COMMIT=0 \
    CONFIGS=0 \
    CONTAINERS=0 \
    DELETE=0 \
    DISABLE_IPV6=0 \
    DISTRIBUTION=0 \
    EVENTS=1 \
    EXEC=0 \
    GRPC=0 \
    IMAGES=0 \
    INFO=0 \
    LOG_LEVEL=info \
    NETWORKS=0 \
    NODES=0 \
    PATCH=0 \
    PING=1 \
    PLUGINS=0 \
    POST=0 \
    PUT=0 \
    SECRETS=0 \
    SERVICES=0 \
    SESSION=0 \
    SOCKET_PATH=/var/run/docker.sock \
    SWARM=0 \
    SYSTEM=0 \
    TASKS=0 \
    VERSION=1 \
    VOLUMES=0
COPY system_files/ /
RUN touch /var/lib/haproxy/server-state
USER root
CMD ["haproxy", "-f", "/tmp/haproxy.cfg"]
