import json
import os
from contextlib import contextmanager
from logging import info
from pathlib import Path

import pytest
from plumbum import local
from plumbum.cmd import docker

DOCKER_IMAGE_NAME = os.environ.get("DOCKER_IMAGE_NAME", "docker-socket-proxy:local")


def pytest_addoption(parser):
    """Allow prebuilding image for local testing."""
    parser.addoption("--prebuild", action="store_const", const=True)


@pytest.fixture(autouse=True, scope="session")
def prebuild_docker_image(request):
    """Build local docker image once before starting test suite."""
    if request.config.getoption("--prebuild"):
        info(f"Building {DOCKER_IMAGE_NAME}...")
        docker("build", "-t", DOCKER_IMAGE_NAME, Path(__file__).parent.parent)


@contextmanager
def proxy(**env_vars):
    """A context manager that starts the proxy with the specified env.

    While inside the block, `$DOCKER_HOST` will be modified to talk to the proxy
    instead of the raw docker socket.
    """
    container_id = None
    env_list = [f"--env={key}={value}" for key, value in env_vars.items()]
    info(f"Starting {DOCKER_IMAGE_NAME} container with: {env_list}")
    try:
        container_id = docker(
            "container",
            "run",
            "--detach",
            "--privileged",
            "--publish=2375",
            "--volume=/var/run/docker.sock:/var/run/docker.sock",
            *env_list,
            DOCKER_IMAGE_NAME,
        ).strip()
        container_data = json.loads(
            docker("container", "inspect", container_id.strip())
        )
        socket_port = container_data[0]["NetworkSettings"]["Ports"]["2375/tcp"][0][
            "HostPort"
        ]
        with local.env(DOCKER_HOST=f"tcp://localhost:{socket_port}"):
            yield container_id
    finally:
        if container_id:
            info(f"Removing {container_id}...")
            docker(
                "container",
                "rm",
                "-f",
                container_id,
            )
