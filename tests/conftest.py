import json
import os
from contextlib import contextmanager
from logging import info

from plumbum import local
from plumbum.cmd import docker

DOCKER_REPO = os.environ.get("DOCKER_REPO", "docker-socket-proxy")
IMAGE_NAME = f"{DOCKER_REPO}:local"


@contextmanager
def proxy(**env_vars):
    """A context manager that starts the proxy with the specified env.

    While inside the block, `$DOCKER_HOST` will be modified to talk to the proxy
    instead of the raw docker socket.
    """
    container_id = None
    env_list = [f"--env={key}={value}" for key, value in env_vars.items()]
    info(f"Starting {IMAGE_NAME} container with: {env_list}")
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
