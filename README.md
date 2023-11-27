[![Last image-template](https://img.shields.io/badge/last%20template%20update-v0.1.3-informational)](https://github.com/Tecnativa/image-template/tree/v0.1.3)
[![GitHub Container Registry](https://img.shields.io/badge/GitHub%20Container%20Registry-latest-%2324292e)](https://github.com/orgs/Tecnativa/packages/container/package/docker-socket-proxy)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-latest-%23099cec)](https://hub.docker.com/r/tecnativa/docker-socket-proxy)

# Docker Socket Proxy

## What?

This is a security-enhanced proxy for the Docker Socket.

## Why?

Giving access to your Docker socket could mean giving root access to your host, or even
to your whole swarm, but some services require hooking into that socket to react to
events, etc. Using this proxy lets you block anything you consider those services should
not do.

## How?

We use the official [Alpine][]-based [HAProxy][] image with a small configuration file.

It blocks access to the Docker socket API according to the environment variables you
set. It returns a `HTTP 403 Forbidden` status for those dangerous requests that should
never happen.

## Security recommendations

-   Never expose this container's port to a public network. Only to a Docker networks
    where only reside the proxy itself and the service that uses it.
-   Revoke access to any API section that you consider your service should not need.
-   This image does not include TLS support, just plain HTTP proxy to the host Docker
    Unix socket (which is not TLS protected even if you configured your host for TLS
    protection). This is by design because you are supposed to restrict access to it
    through Docker's built-in firewall.
-   [Read the docs](#supported-api-versions) for the API version you are using, and
    **know what you are doing**.

## Usage

1.  Run the API proxy (`--privileged` flag is required here because it connects with the
    docker socket, which is a privileged connection in some SELinux/AppArmor contexts
    and would get locked otherwise):

        $ docker container run \
            -d --privileged \
            --name dockerproxy \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -p 127.0.0.1:2375:2375 \
            tecnativa/docker-socket-proxy

2.  Connect your local docker client to that socket:

        $ export DOCKER_HOST=tcp://localhost:2375

3.  You can see the docker version:

        $ docker version
        Client:
         Version:      17.03.1-ce
         API version:  1.27
         Go version:   go1.7.5
         Git commit:   c6d412e
         Built:        Mon Mar 27 17:14:43 2017
         OS/Arch:      linux/amd64

        Server:
         Version:      17.03.1-ce
         API version:  1.27 (minimum version 1.12)
         Go version:   go1.7.5
         Git commit:   c6d412e
         Built:        Mon Mar 27 17:14:43 2017
         OS/Arch:      linux/amd64
         Experimental: false

4.  You cannot see running containers:

        $ docker container ls
        Error response from daemon: <html><body><h1>403 Forbidden</h1>
        Request forbidden by administrative rules.
        </body></html>

The same will happen to any containers that use this proxy's `2375` port to access the
Docker socket API.

## Grant or revoke access to certain API sections

You grant and revoke access to certain features of the Docker API through environment
variables.

Normally the variables match the URL prefix (i.e. `AUTH` blocks access to `/auth/*`
parts of the API, etc.).

Possible values for these variables:

-   `0` to **revoke** access.
-   `1` to **grant** access.

### Access granted by default

These API sections are mostly harmless and almost required for any service that uses the
API, so they are granted by default.

-   `EVENTS`
-   `PING`
-   `VERSION`

### Access revoked by default

#### Security-critical

These API sections are considered security-critical, and thus access is revoked by
default. Maximum caution when enabling these.

-   `AUTH`
-   `SECRETS`
-   `POST`: When disabled, only `GET` and `HEAD` operations are allowed, meaning any
    section of the API is read-only.

#### Not always needed

You will possibly need to grant access to some of these API sections, which are not so
extremely critical but can expose some information that your service does not need.

-   `BUILD`
-   `COMMIT`
-   `CONFIGS`
-   `CONTAINERS`
-   `ALLOW_START` (containers/`id`/`start`)
-   `ALLOW_STOP` (containers/`id`/`stop`)
-   `ALLOW_RESTARTS` (containers/`id`/`stop`|`restart`|`kill`)
-   `DISTRIBUTION`
-   `EXEC`
-   `GRPC`
-   `IMAGES`
-   `INFO`
-   `NETWORKS`
-   `NODES`
-   `PLUGINS`
-   `SERVICES`
-   `SESSION`
-   `SWARM`
-   `SYSTEM`
-   `TASKS`
-   `VOLUMES`

## Use a different Docker socket location

If your OS stores its Docker socket in a different location and you are unable to bind
mount it in your container specification, you can specify this via the `SOCKET_PATH`
environment variable.

For example, [balenaOS](https://www.balena.io/os/) exposes its socket at
`/var/run/balena-engine.sock`. To accommodate this, merely set the `SOCKET_PATH`
environment variable to `/var/run/balena-engine.sock`.

## Development

All the dependencies you need to develop this project (apart from Docker itself) are
managed with [poetry](https://python-poetry.org/).

To set up your development environment, run:

```
poetry install
```

### Testing

To run the tests locally, add `--prebuild` to autobuild the image before testing:

```sh
poetry run pytest --prebuild
```

By default, the image that the tests use (and optionally prebuild) is named
`docker-socket-proxy:local`. If you prefer, you can build it separately before testing,
and remove the `--prebuild` flag, to run the tests with that image you built:

```sh
docker image build -t docker-socket-proxy:local .
poetry run pytest
```

If you want to use a different image, export the `DOCKER_IMAGE_NAME` env variable with
the name you want:

```sh
# To build it automatically
env DOCKER_IMAGE_NAME=my_custom_image poetry run pytest --prebuild

# To prebuild it separately
docker image build -t my_custom_image .
env DOCKER_IMAGE_NAME=my_custom_image poetry run pytest
```

## Logging

You can set the logging level or severity level of the messages to be logged with the
environment variable `LOG_LEVEL`. Default value is info. Possible values are: debug,
info, notice, warning, err, crit, alert and emerg.

## Supported API versions

-   [1.27](https://docs.docker.com/engine/api/v1.27/)
-   [1.28](https://docs.docker.com/engine/api/v1.28/)
-   [1.29](https://docs.docker.com/engine/api/v1.29/)
-   [1.30](https://docs.docker.com/engine/api/v1.30/)
-   [1.37](https://docs.docker.com/engine/api/v1.37/)

## Image tags

Right now, the only supported tags in our container images are the ones following this
rules:

1. Each individual git released version will result in an image being tagged with the
   correspondent `:{{version}}`
1. `:latest` will refer to the latest _released_ version in git.
1. `:edge` will be the version that is in the repo's master branch

Any other tag you find in our [Docker Hub image][dh-img] is deprecated.

We recommend using [GitHub Container Registry][ghcr-img] instead.

## Feedback

Please send any issues to the [issue tracker][]. For other kind of feedback, you can use
[our forum][].

[alpine]: https://alpinelinux.org/
[dh-img]: https://hub.docker.com/r/tecnativa/docker-socket-proxy
[ghcr-img]:
    https://github.com/orgs/Tecnativa/packages/container/package/docker-socket-proxy
[haproxy]: http://www.haproxy.org/
[issue tracker]: https://github.com/Tecnativa/docker-socket-proxy/issues
[our forum]: https://github.com/Tecnativa/docker-socket-proxy/discussions
