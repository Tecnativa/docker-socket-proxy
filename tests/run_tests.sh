#!/bin/bash

set -eu

proxy_container=docksockprox_test
socket_proxy=127.0.0.1:2375

start_proxy() {
    echo "Starting $proxy_container with args: ${*}..."
    docker run -d --name "$proxy_container" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -p "${socket_proxy}:2375" \
        "$@" \
        tecnativa/docker-socket-proxy &>/dev/null
}

delete_proxy() {
    echo "Removing ${proxy_container}..."
    docker rm -f "$proxy_container" &>/dev/null
}

docker_with_proxy() {
    docker --host "$socket_proxy" "$@" 2>&1
}

assert() {
    assertion=$1
    shift 1
    if docker_with_proxy "$@" | grep -qi 'forbidden'; then
        result='forbidden'
    else
        result='allowed'
    fi
    if [ "$assertion" == "$result" ]; then
        printf '%s' 'PASS'
    else
        printf '%s' 'FAIL'
    fi
    echo " | assert 'docker $*' is $assertion"
}


trap delete_proxy EXIT

start_proxy
assert allowed   version
assert forbidden run --rm alpine
assert forbidden pull alpine
assert forbidden logs "$proxy_container"
assert forbidden wait "$proxy_container"
assert forbidden rm -f "$proxy_container"
assert forbidden restart "$proxy_container"
assert forbidden network ls
assert forbidden config ls
assert forbidden service ls
assert forbidden stack ls
assert forbidden secret ls
assert forbidden plugin ls
assert forbidden info
assert forbidden system info
assert forbidden build .
assert forbidden swarm init

delete_proxy
start_proxy -e CONTAINERS=1
assert allowed   logs "$proxy_container"
assert allowed   inspect "$proxy_container"
assert forbidden wait "$proxy_container"
assert forbidden run --rm alpine
assert forbidden rm -f "$proxy_container"
assert forbidden restart "$proxy_container"

delete_proxy
start_proxy -e POST=1
assert forbidden rm -f "$proxy_container"
assert forbidden pull alpine
assert forbidden run --rm alpine
assert forbidden network create foobar

delete_proxy
start_proxy -e NETWORKS=1 -e POST=1
assert allowed network ls
assert allowed network create foo
assert allowed network rm foo
