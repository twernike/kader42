#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for ethernet device..."

# Max 30 Sekunden warten
for i in {1..30}; do
    devs=$(nmcli -t -f DEVICE,TYPE device | grep ':ethernet' | cut -d: -f1 || true)
    if [ -n "$devs" ]; then
        break
    fi
    sleep 1
done

if [ -z "$devs" ]; then
    echo "No ethernet device found, aborting."
    exit 0
fi

echo "Ethernet devices found: $devs"

# Nur Ethernet-Verbindungen löschen (nicht lo!)
nmcli -t -f NAME,TYPE connection show \
  | grep ':ethernet' \
  | cut -d: -f1 \
  | while read -r con; do
        nmcli connection delete "$con" || true
    done

# Devices verbinden
for dev in $devs; do
    nmcli device connect "$dev" || true
done
