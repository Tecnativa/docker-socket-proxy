#!/bin/sh

set -e

# Create a group with the same gid as the docker socket
export DOCKER_GID=$(stat -c "%g" $SOCKET_PATH)
addgroup -g $DOCKER_GID docker

# Run the original entrypoint - Our work here is done.
exec /usr/local/bin/docker-entrypoint.sh $@
