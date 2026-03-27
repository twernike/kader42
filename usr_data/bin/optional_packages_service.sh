#!/bin/bash

# Zielverzeichnis erstellen
sudo mkdir -p /etc/kader42
CONF_FILE="/etc/kader42/optional_packages.conf"

# Datei leeren, falls sie existiert
> "$CONF_FILE"

# Die Reihenfolge der IDs MUSS exakt der Reihenfolge der arguments in der .conf entsprechen
PACKAGE_IDS=("google-chrome" "visual-studio-code-bin")
ARGUMENTS=("$@")

for i in "${!PACKAGE_IDS[@]}"; do
    # Calamares liefert den String "true" für ausgewählte Pakete
    if [[ "${ARGUMENTS[i]}" == "true" ]]; then
        echo "${PACKAGE_IDS[i]}=t" >> "$CONF_FILE"
    fi
done