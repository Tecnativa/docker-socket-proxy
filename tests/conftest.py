import json
from contextlib import contextmanager
from logging import info
from pathlib import Path

import pytest
from plumbum import local
from plumbum.cmd import docker

IMAGE_NAME = "docker-socket-proxy:local"


@pytest.fixture(autouse=True, scope="session")
def docker_image():
    """Build local docker image once before starting test suite."""
    info(f"Building {IMAGE_NAME}...")
    docker("build", "-t", IMAGE_NAME, Path(__file__).parent.parent)
    return IMAGE_NAME


@pytest.fixture()
def sleeping_container():
    """Launch a test container that will last alive as long as the test."""
    try:
        container = docker(
            "container", "run", "--rm", "--detach", "alpine", "sleep", "3600"
        ).strip()
        yield container
    finally:
        docker("container", "rm", "--force", container)


@contextmanager
def proxy(**env_vars):
    """A context manager that starts the proxy with the specified env.

    While inside the block, `$DOCKER_HOST` will be modified to talk to the proxy
    instead of the raw docker socket.
    """
    container_id = None
    env_list = [f"--env={key}={value}" for key, value in env_vars.items()]
    info(f"Starting {IMAGE_NAME} container with: {env_vars.join(' ')}")
    try:
        container_id = docker(
            "container",
            "run",
            "--detach",
            "--privileged",
            "--publish=2375",
            "--volume=/var/run/docker.sock:/var/run/docker.sock",
            *env_list,
            IMAGE_NAME,
        )
        container_data = json.loads(
            docker("container", "inspect", container_id.strip())
        )
        socket_port = container_data[0]["NetworkSettings"]["Ports"]["2375/tcp"][0][
            "HostPort"
        ]
        with local.env(DOCKER_HOST=f"tcp://localhost:{socket_port}"):
            yield
    finally:
        if container_id:
            info(f"Removing {container_id}...")
            docker(
                "container",
                "rm",
                "-f",
                container_id,
            )
