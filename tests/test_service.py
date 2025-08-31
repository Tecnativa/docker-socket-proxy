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
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_network_delete_permissions(proxy_factory):
    with proxy_factory(NETWORKS=1, DELETE=1):
        allowed_calls = [
            ("network", "rm", "foo"),
            ("network", "rm", "-f", "foobarfoo"),
        ]
        forbidden_calls = [
            ("network", "create", "foobarfoo"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_network_delete_permissions_v2(proxy_factory):
    with proxy_factory(NETWORKS=1, POST=1):
        allowed_calls = [
            ("network", "create", "foobarfoo"),
        ]
        forbidden_calls = [
            ("network", "rm", "foobarfoo"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_exec_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1) as container_id:
        allowed_calls = [
            ("exec", container_id, "ls"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_image_delete_permissions_v1(proxy_factory):
    with proxy_factory(DELETE=1, ALLOW_IMAGES_DELETE=1, IMAGES=1, POST=1):
        allowed_calls = [
            ("pull", "alpine"),
            ("image", "rmi", "alpine"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_image_delete_permissions_v2(proxy_factory):
    with proxy_factory(IMAGES=1, POST=1, DELETE=1):
        allowed_calls = [
            ("pull", "alpine"),
            ("image", "ls"),
            ("image", "inspect", "alpine"),
        ]
        forbidden_calls = [
            ("image", "rmi", "alpine"),
            ("image", "rmi", "-f", "alpine"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_container_delete_permissions_v2(proxy_factory):
    with proxy_factory(
        CONTAINERS=1,
        DELETE=1,
        ALLOW_START=1,
        ALLOW_CONTAINERS_DELETE=1,
        IMAGES=1,
        POST=1,
    ):
        allowed_calls = [
            ("pull", "alpine"),
            ("container", "run", "-dt", "--rm", "--name", "alpine", "alpine"),
            ("container", "rm", "-f", "alpine"),
            # ("image", "rmi", "alpine"),
            # ("image", "rmi", "-f", "alpine"),
        ]
        forbidden_calls = [
            ("image", "rmi", "alpine"),
            ("image", "rmi", "-f", "alpine"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)
