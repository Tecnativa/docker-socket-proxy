#!/bin/sh
set -e

# Raise default nofile limit for HAProxy v3
ulimit -n 10000 2>/dev/null || true

is_true() {
	case "$(echo "$1" | tr '[:upper:]' '[:lower:]')" in
		1|true|yes)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

if [ -z "$BIND_PORT" ]; then
	if is_true "$TLS"; then
		BIND_PORT=2376
	else
		BIND_PORT=2375
	fi
fi

if [ -z "$BIND_CONFIG" ]; then
	if is_true "$DISABLE_IPV6"; then
		BIND_ADDRESS=":$BIND_PORT"
	else
		BIND_ADDRESS="[::]:$BIND_PORT v4v6"
	fi

	if is_true "$TLS"; then
		if [ -z "$TLS_CERT_PATH" ]; then
			echo >&2 "TLS is enabled but TLS_CERT_PATH is not set."
			exit 1
		fi
		if [ ! -f "$TLS_CERT_PATH" ]; then
			echo >&2 "TLS certificate file not found: $TLS_CERT_PATH"
			exit 1
		fi
		BIND_CONFIG="$BIND_ADDRESS ssl crt $TLS_CERT_PATH"

		if is_true "$TLS_VERIFY_CLIENT"; then
			if [ -z "$TLS_CLIENT_CA_CERT_PATH" ]; then
				echo >&2 "Client certificate verification is enabled but TLS_CLIENT_CA_CERT_PATH is not set."
				exit 1
			fi
			if [ ! -f "$TLS_CLIENT_CA_CERT_PATH" ]; then
				echo >&2 "Client CA file not found: $TLS_CLIENT_CA_CERT_PATH"
				exit 1
			fi
			BIND_CONFIG="$BIND_CONFIG verify required ca-file $TLS_CLIENT_CA_CERT_PATH"
		fi
	else
		BIND_CONFIG="$BIND_ADDRESS"
	fi
fi

# Process the HAProxy configuration template using sed
sed "s|\${BIND_CONFIG}|$BIND_CONFIG|g" /usr/local/etc/haproxy/haproxy.cfg.template > /tmp/haproxy.cfg

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
