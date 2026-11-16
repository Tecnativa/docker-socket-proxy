import logging
import time
from contextlib import contextmanager

import pytest
from plumbum import local
from python_on_whales import Container, docker

_logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Allow prebuilding image for local testing."""
    parser.addoption(
        "--prebuild", action="store_true", help="Build local image before testing"
    )
    parser.addoption(
        "--image",
        action="store",
        default="tecnativa/docker-socket-proxy:lts-testonly",
        help="Specify testing image name",
    )


@pytest.fixture(scope="session")
def image(request):
    """Get image name. Builds it if needed."""
    image = request.config.getoption("--image")
    if request.config.getoption("--prebuild"):
        docker.buildx.bake(
            files=[request.config.rootpath / "docker-bake.hcl"],
            load=True,
            variables={
                "TAG_SUFFIX": "-testonly",
            },
        )
    return image


@pytest.fixture(scope="session")
def proxy_factory(image):
    """A context manager that starts the proxy with the specified env.

    While inside the block, `$DOCKER_HOST` will be modified to talk to the proxy
    instead of the raw docker socket.
    """

    @contextmanager
    def _proxy(**env_vars):
        _logger.info(f"Starting {image} container with: {env_vars}")
        container = None
        try:
            container: Container = docker.container.run(
                detach=True,
                privileged=True,
                publish=[
                    (2375,),
                ],
                volumes=[
                    ("/var/run/docker.sock", "/var/run/docker.sock"),
                ],
                envs=env_vars,
                image=image,
            )
            time.sleep(0.5)
            socket_port = container.network_settings.ports["2375/tcp"][0]["HostPort"]
            with local.env(DOCKER_HOST=f"tcp://localhost:{socket_port}"):
                yield container.id
        finally:
            if container:
                _logger.info(f"Removing {container.id}...")
                container.remove(force=True)

    return _proxy
