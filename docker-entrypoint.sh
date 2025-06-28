#!/bin/sh
set -e

# Normalize the input for DISABLE_IPV6 to lowercase
DISABLE_IPV6_LOWER=$(echo "$DISABLE_IPV6" | tr '[:upper:]' '[:lower:]')

# Check for different representations of 'true' and set BIND_PORT and BIND_OPTIONS accordingly
case "$DISABLE_IPV6_LOWER" in
    1|true|yes)
        export BIND_PORT=':2375'
        export BIND_OPTIONS=''
        ;;
    *)
        export BIND_PORT=':::2375'
        export BIND_OPTIONS='v4v6'
        ;;
esac

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
