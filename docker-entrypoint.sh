#!/bin/sh
set -e

# Raise default nofile limit for HAProxy v3
ulimit -n 10000 2>/dev/null || true

# Normalize the input for DISABLE_IPV6 to lowercase
DISABLE_IPV6_LOWER=$(echo "$DISABLE_IPV6" | tr '[:upper:]' '[:lower:]')

# Check for different representations of 'true' and set BIND_CONFIG
case "$DISABLE_IPV6_LOWER" in
    1|true|yes)
        BIND_CONFIG=":2375"
        ;;
    *)
        BIND_CONFIG="[::]:2375 v4v6"
        ;;
esac

# Process the HAProxy configuration template using sed
sed "s/\${BIND_CONFIG}/$BIND_CONFIG/g" /usr/local/etc/haproxy/haproxy.cfg.template > /tmp/haproxy.cfg

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
	set -- haproxy "$@"
fi

if [ "$1" = 'haproxy' ]; then
	shift # "haproxy"
	# if the user wants "haproxy", let's add a couple useful flags
	#   -W  -- "master-worker mode" (similar to the old "haproxy-systemd-wrapper"; allows for reload via "SIGUSR2")
	#   -db -- disables background mode
	set -- haproxy -W -db "$@"
fi

exec "$@"
