import logging

from plumbum import ProcessExecutionError
from plumbum.cmd import docker

logger = logging.getLogger()

CONTAINER_NAME = "docksockprox_test"
SOCKET_PROXY = "127.0.0.1:2375"


def _start_proxy(
    container_name=CONTAINER_NAME, socket_proxy=SOCKET_PROXY, extra_args=None
):
    logger.info(f"Starting {container_name} with args: {extra_args}...")
    docker(
        "run",
        "-d",
        "--name",
        container_name,
        "--privileged",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-p",
        f"{socket_proxy}:2375",
        extra_args,
        "tecnativa/docker-socket-proxy",
    )


def _stop_and_delete_proxy(
    container_name=CONTAINER_NAME,
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


def _check_permission(assertion, socket_proxy=SOCKET_PROXY, extra_args=None):
    if "forbidden" in _query_docker_with_proxy(
        socket_proxy=socket_proxy, extra_args=extra_args
    ):
        result = "forbidden"
    else:
        result = "allowed"
    assert result == assertion


def test_default_permissions():
    container_name = f"{CONTAINER_NAME}_1"
    socket_proxy = "127.0.0.1:2375"
    try:
        _start_proxy(container_name=container_name, socket_proxy=socket_proxy)
        _check_permission("allowed", socket_proxy=socket_proxy, extra_args="version")
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["run", "--rm", "alpine"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["pull", "alpine"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["logs", container_name]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["wait", container_name]
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["rm", "-f", container_name],
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["restart", container_name],
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["network", "ls"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["config", "ls"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["service", "ls"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["stack", "ls"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["secret", "ls"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["plugin", "ls"]
        )
        _check_permission("forbidden", socket_proxy=socket_proxy, extra_args=["info"])
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["system", "info"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["build", "."]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["swarm", "init"]
        )
    finally:
        _stop_and_delete_proxy(container_name=container_name)


def test_container_permissions():
    container_name = f"{CONTAINER_NAME}_2"
    socket_proxy = "127.0.0.1:2376"
    try:
        _start_proxy(
            container_name=container_name,
            socket_proxy=socket_proxy,
            extra_args=["-e", "CONTAINERS=1"],
        )
        _check_permission(
            "allowed", socket_proxy=socket_proxy, extra_args=["logs", container_name]
        )
        _check_permission(
            "allowed", socket_proxy=socket_proxy, extra_args=["inspect", container_name]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["wait", container_name]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["run", "--rm", "alpine"]
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["rm", "-f", container_name],
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["restart", container_name],
        )
    finally:
        _stop_and_delete_proxy(container_name=container_name)


def test_post_permissions():
    container_name = f"{CONTAINER_NAME}_3"
    socket_proxy = "127.0.0.1:2377"
    try:
        _start_proxy(
            container_name=container_name,
            socket_proxy=socket_proxy,
            extra_args=["-e", "POST=1"],
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["rm", "-f", container_name],
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["pull", "alpine"]
        )
        _check_permission(
            "forbidden", socket_proxy=socket_proxy, extra_args=["run", "--rm", "alpine"]
        )
        _check_permission(
            "forbidden",
            socket_proxy=socket_proxy,
            extra_args=["network", "create", "foobar"],
        )
    finally:
        _stop_and_delete_proxy(container_name=container_name)


def test_network_post_permissions():
    container_name = f"{CONTAINER_NAME}_4"
    socket_proxy = "127.0.0.1:2378"
    try:
        _start_proxy(
            container_name=container_name,
            socket_proxy=socket_proxy,
            extra_args=["-e", "POST=1", "-e", "NETWORKS=1"],
        )
        _check_permission(
            "allowed", socket_proxy=socket_proxy, extra_args=["network", "ls"]
        )
        _check_permission(
            "allowed",
            socket_proxy=socket_proxy,
            extra_args=["network", "create", "foo"],
        )
        _check_permission(
            "allowed", socket_proxy=socket_proxy, extra_args=["network", "rm", "foo"]
        )
    finally:
        _stop_and_delete_proxy(container_name=container_name)
