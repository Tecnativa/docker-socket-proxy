import logging
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
from plumbum import ProcessExecutionError, local
from plumbum.cmd import docker

logger = logging.getLogger()


def _check_permissions(allowed_calls, forbidden_calls):
    for args in allowed_calls:
        docker(*args)
    for args in forbidden_calls:
        with pytest.raises(ProcessExecutionError):
            docker(*args)


def _proxy_status(path):
    url = local.env["DOCKER_HOST"].replace("tcp://", "http://", 1) + path
    try:
        with urlopen(url) as response:
            return response.status
    except HTTPError as error:
        return error.code


def _check_paths(allowed_paths, forbidden_paths):
    # Docker answers libpod paths with its own error, so only a 403 is the proxy.
    for path in allowed_paths:
        assert _proxy_status(path) != 403, path
    for path in forbidden_paths:
        assert _proxy_status(path) == 403, path


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


def test_exec_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1) as container_id:
        allowed_calls = [
            ("exec", container_id, "ls"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_libpod_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1):
        allowed_paths = [
            "/v4.6.1/libpod/_ping",
            "/v4.6.1/libpod/version",
            "/v4.6.1/libpod/containers/json",
            "/libpod/containers/json",
        ]
        forbidden_paths = [
            "/v4.6.1/libpod/images/json",
            "/v4.6.1/libpod/info",
            "/v4.6.1/libpod/pods/json",
            "/v4.6.1/other/containers/json",
        ]
        _check_paths(allowed_paths, forbidden_paths)


def test_libpod_routes_beyond_docker_blocked(proxy_factory):
    with proxy_factory(IMAGES=1, SECRETS=1, SYSTEM=1, VOLUMES=1):
        allowed_paths = [
            "/v4.6.1/libpod/secrets/json",
            "/v4.6.1/libpod/system/df",
            "/v4.6.1/libpod/volumes/json",
        ]
        forbidden_paths = [
            "/v4.6.1/libpod/secrets/foo/json",
            "/v4.6.1/libpod/volumes/foo/export",
            "/v4.6.1/libpod/system/prune",
            "/v4.6.1/libpod/images/scp/foo",
        ]
        _check_paths(allowed_paths, forbidden_paths)
