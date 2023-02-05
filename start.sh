#!/bin/sh
openssl req -nodes -new -x509 -subj '/CN=*' -sha256 -keyout /etc/privkey.pem -out /etc/fullchain.pem -days 365000 > /dev/null 2>&1
cat /etc/fullchain.pem /etc/privkey.pem | tee /etc/cert.pem > /dev/null 2>&1
haproxy -f /usr/local/etc/haproxy/haproxy.cfg