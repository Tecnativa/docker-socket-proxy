import json
import logging
from contextlib import contextmanager

import pytest
from plumbum import ProcessExecutionError, local
from plumbum.cmd import docker

logger = logging.getLogger()

CONTAINER_NAME = "docksockprox_test"
SOCKET_PROXY = "127.0.0.1:2375"


@pytest.fixture(autouse=True)
def build_docker_image():
    logger.info("Building docker image...")
    docker("build", "-t", "docker-socket-proxy:local", ".")


def _start_proxy(env_vars_list):
    logger.info(f"Starting docker-socket-proxy container with args: {env_vars_list}...")
    # HACK: receive as array to make it easier to handle dynamic env vars for docker
    cmd = [
        "run",
        "-d",
        "--privileged",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-p",
        "2375",
    ]
    cmd.extend(env_vars_list)
    cmd.append("docker-socket-proxy:local")
    ret_code, stdout, stderr = docker.run(cmd)
    # Get container info
    container_id = stdout.strip()
    container_data = json.loads(docker("inspect", container_id))
    socket_port = container_data[0]["NetworkSettings"]["Ports"]["2375/tcp"][0][
        "HostPort"
    ]
    return container_id, socket_port


def _stop_and_delete_proxy(container):
    logger.info(f"Removing {container}...")
    docker(
        "container",
        "rm",
        "-f",
        container,
    )


@contextmanager
def _docker_proxy(**env_vars):
    env_vars_list = []
    for var in env_vars:
        env_vars_list.extend(["-e", f"{var}={env_vars[var]}"])
    container, port = _start_proxy(env_vars_list)
    # start a test container for queries
    test_container = docker("run", "--rm", "-d", "nginx").strip()
    try:
        with local.env(DOCKER_HOST=f"127.0.0.1:{port}"):
            yield (docker, test_container)
    finally:
        _stop_and_delete_proxy(container)
        docker("stop", test_container)


def _query_docker_with_proxy(*command, allowed=True):
    if allowed:
        docker(command)
    else:
        with pytest.raises(ProcessExecutionError):
            docker(command)


def test_default_permissions():
    with _docker_proxy() as (docker, test_container):
        _query_docker_with_proxy("version", allowed=True)
        _query_docker_with_proxy("pull", "alpine", allowed=False)
        _query_docker_with_proxy(
            "run", "--rm", "alpine", "--name", test_container, allowed=False
        )
        _query_docker_with_proxy("logs", test_container, allowed=False)
        _query_docker_with_proxy("wait", test_container, allowed=False)
        _query_docker_with_proxy("rm", "-f", test_container, allowed=False)
        _query_docker_with_proxy("restart", test_container, allowed=False)
        _query_docker_with_proxy("network", "ls", allowed=False)
        _query_docker_with_proxy("config", "ls", allowed=False)
        _query_docker_with_proxy("service", "ls", allowed=False)
        _query_docker_with_proxy("stack", "ls", allowed=False)
        _query_docker_with_proxy("secret", "ls", allowed=False)
        _query_docker_with_proxy("plugin", "ls", allowed=False)
        _query_docker_with_proxy("info", allowed=False)
        _query_docker_with_proxy("system", "info", allowed=False)
        _query_docker_with_proxy("build", ".", allowed=False)
        _query_docker_with_proxy("swarm", "init", allowed=False)


def test_container_permissions():
    with _docker_proxy(CONTAINERS=1) as (docker, test_container):
        _query_docker_with_proxy("logs", test_container, allowed=True)
        _query_docker_with_proxy("inspect", test_container, allowed=True)
        _query_docker_with_proxy("wait", test_container, allowed=False)
        _query_docker_with_proxy("run", "--rm", "alpine", allowed=False)
        _query_docker_with_proxy("rm", "-f", test_container, allowed=False)
        _query_docker_with_proxy("restart", test_container, allowed=False)


def test_post_permissions():
    with _docker_proxy(POST=1) as (docker, test_container):
        _query_docker_with_proxy("rm", "-f", test_container, allowed=False)
        _query_docker_with_proxy("pull", "alpine", allowed=False)
        _query_docker_with_proxy("run", "--rm", "alpine", allowed=False)
        _query_docker_with_proxy("network", "create", "foobar", allowed=False)


def test_network_post_permissions():
    with _docker_proxy(POST=1, NETWORKS=1) as (docker, test_container):
        _query_docker_with_proxy("network", "ls", allowed=True)
        _query_docker_with_proxy("network", "create", "foo", allowed=True)
        _query_docker_with_proxy("network", "rm", "foo", allowed=True)
