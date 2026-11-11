#!/bin/sh
IFACE=$1
ACTION=$2

if [ "$ACTION" = "pre-up" ] || [ "$ACTION" = "up" ]; then
    if ethtool --show-eee "$IFACE" >/dev/null 2>&1; then
        ethtool --set-eee "$IFACE" eee off >/dev/null 2>&1
    fi
fi