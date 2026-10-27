import logging

import pytest
from plumbum import ProcessExecutionError
from plumbum.cmd import docker

logger = logging.getLogger()


def _check_permissions(allowed_calls, forbidden_calls):
    for args in allowed_calls:
        docker(*args)
    for args in forbidden_calls:
        with pytest.raises(ProcessExecutionError):
            docker(*args)


def test_default_permissions(proxy_factory):
    with proxy_factory() as test_container:
        allowed_calls = (("version",),)
        forbidden_calls = (
            ("pull", "alpine"),
            ("--rm", "alpine", "--name", test_container),
            ("logs", test_container),
            ("wait", test_container),
            ("rm", "-f", test_container),
            ("restart", test_container),
            ("network", "ls"),
            ("config", "ls"),
            ("service", "ls"),
            ("stack", "ls"),
            ("secret", "ls"),
            ("plugin", "ls"),
            ("info",),
            ("system", "info"),
            ("build", "."),
            ("buildx build", "."),
            ("swarm", "init"),
        )
        _check_permissions(allowed_calls, forbidden_calls)


def test_container_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1) as test_container:
        allowed_calls = [
            ("logs", test_container),
            ("inspect", test_container),
        ]
        forbidden_calls = [
            ("wait", test_container),
            ("run", "--rm", "alpine"),
            ("rm", "-f", test_container),
            ("restart", test_container),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_post_permissions(proxy_factory):
    with proxy_factory(POST=1) as test_container:
        allowed_calls = []
        forbidden_calls = [
            ("rm", "-f", test_container),
            ("pull", "alpine"),
            ("run", "--rm", "alpine"),
            ("network", "create", "foobar"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_network_post_permissions(proxy_factory):
    with proxy_factory(POST=1, NETWORKS=1):
        allowed_calls = [
            ("network", "ls"),
            ("network", "create", "foo"),
            ("network", "rm", "foo"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


@pytest.fixture
def target_container():
    """A container to act on, started directly against the docker socket."""
    container_id = docker(
        "container", "run", "--detach", "alpine", "sleep", "300"
    ).strip()
    try:
        yield container_id
    finally:
        docker("container", "rm", "-f", container_id)


def test_granular_permissions_without_post(proxy_factory, target_container):
    """The ALLOW_* container actions work on their own, without POST=1."""
    with proxy_factory(
        ALLOW_START=1,
        ALLOW_STOP=1,
        ALLOW_RESTARTS=1,
        ALLOW_PAUSE=1,
        ALLOW_UNPAUSE=1,
    ):
        allowed_calls = [
            ("pause", target_container),
            ("unpause", target_container),
            ("restart", "--time", "0", target_container),
            ("stop", "--time", "0", target_container),
            ("start", target_container),
            ("kill", target_container),
        ]
        forbidden_calls = [
            ("rm", "-f", target_container),
            ("run", "--rm", "alpine"),
            ("network", "create", "foobar"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_exec_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1) as container_id:
        allowed_calls = [
            ("exec", container_id, "ls"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)
