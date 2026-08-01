import logging
import subprocess

import pytest
from plumbum import ProcessExecutionError
from plumbum.cmd import docker

logger = logging.getLogger()


def _run_openssl(cert_dir, *args):
    subprocess.run(
        ["openssl", *args],
        cwd=cert_dir,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def tls_certs(tmp_path_factory):
    cert_dir = tmp_path_factory.mktemp("tls-certs")
    _run_openssl(cert_dir, "genrsa", "-out", "ca-key.pem", "2048")
    _run_openssl(
        cert_dir,
        "req",
        "-x509",
        "-new",
        "-key",
        "ca-key.pem",
        "-sha256",
        "-days",
        "3650",
        "-subj",
        "/CN=docker-socket-proxy-test-ca",
        "-out",
        "ca.pem",
    )

    _run_openssl(cert_dir, "genrsa", "-out", "server-key.pem", "2048")
    _run_openssl(
        cert_dir,
        "req",
        "-new",
        "-key",
        "server-key.pem",
        "-subj",
        "/CN=localhost",
        "-out",
        "server.csr",
    )
    (cert_dir / "server-ext.cnf").write_text(
        "subjectAltName=DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth\n",
        encoding="utf-8",
    )
    _run_openssl(
        cert_dir,
        "x509",
        "-req",
        "-in",
        "server.csr",
        "-CA",
        "ca.pem",
        "-CAkey",
        "ca-key.pem",
        "-CAcreateserial",
        "-out",
        "server-cert.pem",
        "-days",
        "3650",
        "-sha256",
        "-extfile",
        "server-ext.cnf",
    )
    (cert_dir / "server.pem").write_text(
        (cert_dir / "server-cert.pem").read_text(encoding="utf-8")
        + (cert_dir / "server-key.pem").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    _run_openssl(cert_dir, "genrsa", "-out", "key.pem", "2048")
    _run_openssl(
        cert_dir,
        "req",
        "-new",
        "-key",
        "key.pem",
        "-subj",
        "/CN=docker-socket-proxy-test-client",
        "-out",
        "client.csr",
    )
    (cert_dir / "client-ext.cnf").write_text(
        "extendedKeyUsage=clientAuth\n",
        encoding="utf-8",
    )
    _run_openssl(
        cert_dir,
        "x509",
        "-req",
        "-in",
        "client.csr",
        "-CA",
        "ca.pem",
        "-CAkey",
        "ca-key.pem",
        "-CAcreateserial",
        "-out",
        "cert.pem",
        "-days",
        "3650",
        "-sha256",
        "-extfile",
        "client-ext.cnf",
    )

    return cert_dir


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


def test_exec_permissions(proxy_factory):
    with proxy_factory(CONTAINERS=1, EXEC=1, POST=1) as container_id:
        allowed_calls = [
            ("exec", container_id, "ls"),
        ]
        forbidden_calls = []
        _check_permissions(allowed_calls, forbidden_calls)


def test_tls_permissions(proxy_factory, tls_certs):
    certs_mount = f"{tls_certs}:/certs:ro"
    tls_docker_env = {
        "DOCKER_CERT_PATH": str(tls_certs),
        "DOCKER_TLS_VERIFY": "1",
    }

    with proxy_factory(
        publish_port=2376,
        mounts=[certs_mount],
        docker_env=tls_docker_env,
        TLS=1,
        TLS_CERT_PATH="/certs/server.pem",
    ):
        allowed_calls = [
            ("version",),
        ]
        forbidden_calls = [
            ("network", "ls"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)


def test_mtls_permissions(proxy_factory, tls_certs):
    certs_mount = f"{tls_certs}:/certs:ro"
    tls_docker_env = {
        "DOCKER_CERT_PATH": str(tls_certs),
        "DOCKER_TLS_VERIFY": "1",
    }

    with proxy_factory(
        publish_port=2376,
        mounts=[certs_mount],
        docker_env=tls_docker_env,
        TLS=1,
        TLS_CERT_PATH="/certs/server.pem",
        TLS_VERIFY_CLIENT=1,
        TLS_CLIENT_CA_CERT_PATH="/certs/ca.pem",
    ):
        allowed_calls = [
            ("version",),
        ]
        forbidden_calls = [
            ("network", "ls"),
        ]
        _check_permissions(allowed_calls, forbidden_calls)
