# Docker Socket Readonly Proxy

[![](https://images.microbadger.com/badges/version/tecnativa/docker-socket-readonly:latest.svg)](https://microbadger.com/images/tecnativa/docker-socket-readonly:latest "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/tecnativa/docker-socket-readonly:latest.svg)](https://microbadger.com/images/tecnativa/docker-socket-readonly:latest "Get your own image badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/tecnativa/docker-socket-readonly:latest.svg)](https://microbadger.com/images/tecnativa/docker-socket-readonly:latest "Get your own commit badge on microbadger.com")
[![](https://images.microbadger.com/badges/license/tecnativa/docker-socket-readonly.svg)](https://microbadger.com/images/tecnativa/docker-socket-readonly "Get your own license badge on microbadger.com")

## What?

This is a readonly proxy for the Docker Socket.

## Why?

Giving access to your Docker socket could mean giving root access to your host,
or even to your whole swarm, but some services require hooking into that socket to
react to events, etc. Using this proxy lets you block anything you consider those services should not do.

## How?

We use the official [Alpine][]-based [HAProxy][] image with a small
configuration file.

It blocks access to the Docker socket [API][] according to the environment
variables you set. It returns a `HTTP 403 Forbidden` status for those dangerous
requests that should never happen.

## Usage


## Feedback

Please send any feedback (issues, questions) to the [issue tracker][].

[Alpine]: https://alpinelinux.org/
[API]: https://docs.docker.com/engine/api/v1.27/
[HAProxy]: http://www.haproxy.org/
[issue tracker]: https://github.com/Tecnativa/docker-socket-proxy/issues
[Odoo]: https://www.odoo.com/
[proxy mode]: https://www.odoo.com/documentation/10.0/reference/cmdline.html#cmdoption-odoo.py--proxy-mode
[worker mode]: https://www.odoo.com/documentation/10.0/setup/deploy.html#worker-number-calculation
