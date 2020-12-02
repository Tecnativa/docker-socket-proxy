import logging

import pytest
from plumbum import ProcessExecutionError
from plumbum.cmd import docker

from .conftest import proxy

logger = logging.getLogger()


def test_default_permissions(sleeping_container):
    allowed_calls = (("version",),)
    forbidden_calls = (
        ("pull", "alpine"),
        ("--rm", "alpine", "--name", sleeping_container),
        ("logs", sleeping_container),
        ("wait", sleeping_container),
        ("rm", "-f", sleeping_container),
        ("restart", sleeping_container),
        ("network", "ls"),
        ("config", "ls"),
        ("service", "ls"),
        ("stack", "ls"),
        ("secret", "ls"),
        ("plugin", "ls"),
        ("info",),
        ("system", "info"),
        ("build", "."),
        ("swarm", "init"),
    )
    with proxy():
        for args in allowed_calls:
            docker(*args)
        for args in forbidden_calls:
            with pytest.raises(ProcessExecutionError):
                docker(*args)


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
