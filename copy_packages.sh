#!/bin/bash
set -e

BUILD_DIR="/build"
LOCAL_REPO="/packages"

mkdir -p "$LOCAL_REPO"

# Liste der AUR-Pakete
PACKAGES=(
    "alpm_octopi_utils-git"
    "calamares-git"
    "yay"
    "plasma-gamemode-git"
    # "waydroid-git"
    # "waydroid-biglinux-git"
    # "waydroid-settings-git"
    "winboat"
    # "heroic-games-launcher-git"
)

# ==============================
# Paketbau
# ==============================
cd "$BUILD_DIR"

for pkg in "${PACKAGES[@]}"; do
    echo "Copy package $pkg"
    # Alle erzeugten Pakete ins Repo-Verzeichnis kopieren
    cp /build/$pkg/*.pkg.tar.zst "$LOCAL_REPO/"
done

# ==============================
# Lokale Repo-DB erstellen/aktualisieren
# ==============================
cd "$LOCAL_REPO"
repo-add custom.db.tar.gz *.pkg.tar.zst

echo "Lokales Repo erfolgreich erstellt in $LOCAL_REPO"