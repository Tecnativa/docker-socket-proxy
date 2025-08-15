#!/bin/sh
set -e

# add haproxy user to group of docker socket
DOCKER_GROUP=$(stat -c %G "$SOCKET_PATH")
adduser haproxy "$DOCKER_GROUP"

# continue as haproxy user, preserving entrypoint parameters
su -s /bin/sh -c 'start-haproxy.sh "$@"' haproxy -- "$@"

