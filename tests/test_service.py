
import pytest
import logging

from plumbum import ProcessExecutionError, local
from plumbum.cmd import docker
from plumbum.machines.local import LocalCommand

logger = logging.getLogger()

CONTAINER_NAME = "docksockprox_test"
SOCKET_PROXY = "127.0.0.1:2375"


def _start_proxy(
    container_name=CONTAINER_NAME,
    socket_proxy=SOCKET_PROXY,
    extra_args=None
):
    logger.info(f"Starting {container_name} with args: {extra_args}...")
    docker(
        "run",
        "-d",
        "--name", container_name,
        "--privileged",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-p", f"{socket_proxy}:2375",
        extra_args,
        "tecnativa/docker-socket-proxy",
    )


def _stop_and_delete_proxy(
    container_name=CONTAINER_NAME,
    socket_proxy=SOCKET_PROXY,
):
    logger.info(f"Removing {container_name}...")
    docker(
        "rm",
        "-f",
        container_name,
    )


def _query_docker_with_proxy(socket_proxy=SOCKET_PROXY, extra_args=None):
    try:
        _ret_code, stdout, stderr = docker.run(
            (
                "--host",
                socket_proxy,
                extra_args,
            )
        )
    except ProcessExecutionError as result:
        stdout = result.stdout
        stderr = result.stderr
    return stdout + stderr


def _check_permission(assertion, extra_args=None):
    if "forbidden" in _query_docker_with_proxy(extra_args=extra_args):
        result = "forbidden"
    else:
        result = "allowed"
    assert result == assertion


def test_default_permissions():
    try:
        _start_proxy()
        _check_permission("allowed", extra_args="version")
        _check_permission("forbidden", ["run", "--rm", "alpine"])
        _check_permission("forbidden", ["pull", "alpine"])
        _check_permission("forbidden", ["logs", CONTAINER_NAME])
        _check_permission("forbidden", ["wait", CONTAINER_NAME])
        _check_permission("forbidden", ["rm", "-f", CONTAINER_NAME])
        _check_permission("forbidden", ["restart", CONTAINER_NAME])
        _check_permission("forbidden", ["network", "ls"])
        _check_permission("forbidden", ["config", "ls"])
        _check_permission("forbidden", ["service", "ls"])
        _check_permission("forbidden", ["stack", "ls"])
        _check_permission("forbidden", ["secret", "ls"])
        _check_permission("forbidden", ["plugin", "ls"])
        _check_permission("forbidden", ["info"])
        _check_permission("forbidden", ["system", "info"])
        _check_permission("forbidden", ["build", "."])
        _check_permission("forbidden", ["swarm", "init"])
    finally:
        pass
        _stop_and_delete_proxy()