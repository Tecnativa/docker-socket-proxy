FROM haproxy:2.2-alpine

EXPOSE 2375
ENV ALLOW_RESTARTS=0 \
    ALLOW_STOP=0 \
    ALLOW_START=0 \
    CONTAINERS_READ=0 \
    CONTAINERS_WRITE=0 \
    EXEC_READ=0 \
    EXEC_WRITE=0 \
    IMAGES_READ=0 \
    IMAGES_WRITE=0 \
    NETWORKS_READ=0 \
    NETWORKS_WRITE=0 \
    SECRETS_READ=0 \
    SECRETS_WRITE=0 \
    SERVICES_READ=0 \
    SERVICES_WRITE=0 \
    VOLUMES_READ=0 \
    VOLUMES_WRITE=0 \
    SWARM_READ=0 \
    SWARM_WRITE=0 \
    NODES_READ=0 \
    NODES_WRITE=0 \
    CONFIGS_READ=0 \
    CONFIGS_WRITE=0 \
    PLUGINS_READ=0 \
    PLUGINS_WRITE=0 \
    SYSTEM_READ=0 \
    SYSTEM_WRITE=0 \
    AUTH=0 \
    BUILD=0 \
    COMMIT=0 \
    DISABLE_IPV6=0 \
    DISTRIBUTION=0 \
    EVENTS=1 \
    GRPC=0 \
    INFO=0 \
    LOG_LEVEL=info \
    PING=1 \
    SESSION=0 \
    SOCKET_PATH=/var/run/docker.sock \
    TASKS=0 \
    VERSION=1

COPY docker-entrypoint.sh /usr/local/bin/
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg.template
COPY verify.lua /usr/local/etc/haproxy/verify.lua
