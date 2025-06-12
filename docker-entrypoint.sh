#!/bin/sh
set -e

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
sed -e "s|\${BIND_CONFIG}|$BIND_CONFIG|g" \
    -e "s|\${TIMEOUT_HTTP_REQUEST}|$TIMEOUT_HTTP_REQUEST|g" \
    -e "s|\${TIMEOUT_QUEUE}|$TIMEOUT_QUEUE|g" \
    -e "s|\${TIMEOUT_CONNECT}|$TIMEOUT_CONNECT|g" \
    -e "s|\${TIMEOUT_CLIENT}|$TIMEOUT_CLIENT|g" \
    -e "s|\${TIMEOUT_SERVER}|$TIMEOUT_SERVER|g" \
    -e "s|\${TIMEOUT_TUNNEL}|$TIMEOUT_TUNNEL|g" \
    /usr/local/etc/haproxy/haproxy.cfg.template > /usr/local/etc/haproxy/haproxy.cfg

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
