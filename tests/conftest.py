import json
import logging
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
from plumbum import local
from plumbum.cmd import docker

_logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Allow prebuilding image for local testing."""
    parser.addoption(
        "--prebuild", action="store_true", help="Build local image before testing"
    )
    parser.addoption(
        "--image",
        action="store",
        default="test:docker-socket-proxy",
        help="Specify testing image name",
    )


@pytest.fixture(scope="session")
def image(request):
    """Get image name. Builds it if needed."""
    image = request.config.getoption("--image")
    if request.config.getoption("--prebuild"):
        build = docker["image", "build", "-t", image, Path(__file__).parent.parent]
        retcode, stdout, stderr = build.run()
        _logger.log(
            # Pytest prints warnings if a test fails, so this is a warning if
            # the build succeeded, to allow debugging the build logs
            logging.ERROR if retcode else logging.WARNING,
            "Build logs for COMMAND: %s\nEXIT CODE:%d\nSTDOUT:%s\nSTDERR:%s",
            build.bound_command(),
            retcode,
            stdout,
            stderr,
        )
        assert not retcode, "Image build failed"
    return image


@pytest.fixture(scope="session")
def proxy_factory(image):
    """A context manager that starts the proxy with the specified env.

    While inside the block, `$DOCKER_HOST` will be modified to talk to the proxy
    instead of the raw docker socket.
    """

    @contextmanager
    def _proxy(publish_port=2375, mounts=None, docker_env=None, **env_vars):
        container_id = None
        env_list = [f"--env={key}={value}" for key, value in env_vars.items()]
        volume_args = ["--volume=/var/run/docker.sock:/var/run/docker.sock"]
        if mounts:
            volume_args.extend([f"--volume={mount}" for mount in mounts])
        _logger.info(f"Starting {image} container with: {env_list}")
        try:
            container_id = docker(
                "container",
                "run",
                "--detach",
                "--privileged",
                f"--publish={publish_port}",
                *volume_args,
                *env_list,
                image,
            ).strip()
            time.sleep(0.5)
            container_data = json.loads(
                docker("container", "inspect", container_id.strip())
            )
            socket_port = container_data[0]["NetworkSettings"]["Ports"][
                f"{publish_port}/tcp"
            ][0][
                "HostPort"
            ]
            env = {"DOCKER_HOST": f"tcp://localhost:{socket_port}"}
            if docker_env:
                env.update(docker_env)
            with local.env(**env):
                yield container_id
        finally:
            if container_id:
                _logger.info(f"Removing {container_id}...")
                docker(
                    "container",
                    "rm",
                    "-f",
                    container_id,
                )

    return _proxy
