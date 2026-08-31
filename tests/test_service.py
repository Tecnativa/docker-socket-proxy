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
            ("inspect", test_container),
        ]
        forbidden_calls = [
            ("logs", test_container),
            ("export", test_container),
            ("cp", f"{test_container}:/etc/passwd", "-"),
            ("wait", test_container),
            ("run", "--rm", "alpine"),
            ("rm", "-f", test_container),
            ("restart", test_container),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_container_logs_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, ALLOW_LOGS=1) as test_container:
        allowed_calls = [
            ("logs", test_container),
            ("inspect", test_container),
        ]
        forbidden_calls = [
            ("export", test_container),
            ("cp", f"{test_container}:/etc/passwd", "-"),
            ("wait", test_container),
            ("run", "--rm", "alpine"),
            ("rm", "-f", test_container),
            ("restart", test_container),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_container_export_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, ALLOW_EXPORT=1) as test_container:
        allowed_calls = [
            ("export", test_container),
            ("inspect", test_container),
        ]
        forbidden_calls = [
            ("logs", test_container),
            ("cp", f"{test_container}:/etc/passwd", "-"),
            ("wait", test_container),
            ("run", "--rm", "alpine"),
            ("rm", "-f", test_container),
            ("restart", test_container),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_container_archive_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, ALLOW_ARCHIVE=1) as test_container:
        allowed_calls = [
            ("cp", f"{test_container}:/etc/passwd", "-"),
            ("inspect", test_container),
        ]
        forbidden_calls = [
            ("logs", test_container),
            ("export", test_container),
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
        forbidden_calls = [
            ("network", "rm", "foo"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)
    docker(["network", "rm", "foo"])


def test_network_delete_permissions(proxy_factory):
    with proxy_factory(NETWORKS=1, POST=1, DELETE=1):
        allowed_calls = [
            ("network", "create", "net-to-delete"),
            ("network", "rm", "net-to-delete"),
        ]
        forbidden_calls = [
            ("volume", "create", "test-volume"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_exec_permissions(proxy_factory):
    # ALLOW_EXEC=1 is required IN ADDITION to CONTAINERS+EXEC+POST to actually
    # create new exec sessions, see issue #114. EXEC controls only operations
    # on already-created exec sessions (/exec/<id>/start|resize|inspect).
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1, ALLOW_EXEC=1) as container_id:
        allowed_calls = [
            ("exec", container_id, "ls"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_exec_denied_without_allow_exec(proxy_factory):
    """CONTAINERS=1 + POST=1 must NOT be enough to create new exec sessions.

    Regression test for https://github.com/Tecnativa/docker-socket-proxy/issues/114.
    """
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1) as container_id:
        forbidden_calls = [
            ("exec", container_id, "ls"),
        ]
        _check_permissions((), forbidden_calls)


def test_kill_denied_without_allow_kill(proxy_factory):
    """CONTAINERS=1 + POST=1 must NOT allow `docker kill`."""
    with proxy_factory(CONTAINERS=1, POST=1) as container_id:
        forbidden_calls = [
            ("kill", container_id),
        ]
        _check_permissions((), forbidden_calls)


def test_delete_denied_without_delete(proxy_factory):
    """CONTAINERS=1 + POST=1 must NOT allow DELETE /containers/<id>."""
    with proxy_factory(CONTAINERS=1, POST=1) as container_id:
        forbidden_calls = [
            ("rm", "-f", container_id),
        ]
        _check_permissions((), forbidden_calls)


def test_container_delete_permissions(proxy_factory):
    with proxy_factory(
        CONTAINERS=1,
        DELETE=1,
        IMAGES=1,
        POST=1,
    ):
        allowed_calls = [
            ("pull", "alpine"),
            ("run", "--rm", "-dt", "--name", "test-delete", "alpine"),
            ("rm", "-f", "test-delete"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_image_delete_permissions(proxy_factory):
    with proxy_factory(IMAGES=1, DELETE=1, POST=1):
        allowed_calls = [
            ("pull", "hello-world"),
            ("image", "rmi", "hello-world"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)
