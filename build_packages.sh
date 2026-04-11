#!/bin/bash

BUILD_DIR="/build"
LOCAL_PACKAGES="/packages"
LOCAL_REPO="$LOCAL_PACKAGES/custom"
DB_FILE="$LOCAL_REPO/custom.db.tar.gz"
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PACKAGES=(
    # "inputactions-ctl"
    # "snapd-glib"
    # "pamac-cli"
    # "asciidoc"
    "calamares"
    # "yay"
    # "libpamac-full"
    "winboat"
    "openboard"
    "inputactions-kwin"
    "pamac-all"
    "pamac-tray-icon-plasma"
    )

check_and_update_repo() {
    echo "Prüfe Repository-Integrität..."
    
    # 1. Alle gebauten Pakete im Verzeichnis finden (nur die Dateinamen)
    mapfile -t LOCAL_PACKAGES < <(find "$LOCAL_REPO" -name "*.pkg.tar.zst" -printf "%f\n")

    for pkg_file in "${LOKALE_PAKETE[@]}"; do
        # Extrahiere Paketnamen (alles vor der ersten Versionsnummer)
        pkg_name=$(echo "$pkg_file" | sed 's/-[0-9].*//')
        
        # Prüfen, ob der Name in der DB existiert
        if ! tar -tf "$DB_FILE" | grep -q "^$pkg_name-"; then
            echo "⚠️  $pkg_name fehlt in der DB. Starte repo-add..."
            
            # 2. Versuch: Paket hinzufügen
            if ! repo-add "$DB_FILE" "$LOCAL_REPO/$pkg_file"; then
                echo "❌ FEHLER: repo-add für $pkg_name fehlgeschlagen!"
                exit 1
            fi
            
            # 3. Finaler Check nach dem zweiten Versuch
            if ! tar -tf "$DB_FILE" | grep -q "^$pkg_name-"; then
                echo "❌ KRITISCH: $pkg_name konnte trotz repo-add nicht indexiert werden!"
                exit 1
            fi
            echo "✅ $pkg_name erfolgreich nachgetragen."
        fi
    done
    echo "🚀 Repository ist konsistent."
}

echo "Install needed dependencies for building packages, if they are not already installed..."
 DEPENDENCIES=(
  "appstream"
  "libnotify" 
  "qt6-declarative"
  "qt6-multimedia"
  "qt6-svg"
  "qt6-webchannel"
  "qt6-webengine"
  "ffmpeg"
  "quazip-qt6"
  "poppler"
  "yaml-cpp"
  "kwin"
  "kcmutils"
  "libadwaita"
  "libhandy"
  "gobject-introspection"
  "meson"
  "vala"
  "ninja"
  "archlinux-appstream-data"
  "dbus-glib"
  "flatpak"
  "json-glib"
  "libsoup3"
  )


for dep in "${DEPENDENCIES[@]}"; do
    if ! pacman -Q "$dep" &>/dev/null; then
        echo -e "\e[1;91m |[build_packages]| Dependency $dep is not installed. Install the dependency...\e[0m"
        sudo pacman -S --noconfirm "$dep"
    fi
done
sudo pacman -Syy --noconfirm

cd "$BUILD_DIR"
git clone "https://aur.archlinux.org/yay.git"
cd "yay"
makepkg -Sf --noconfirm

cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/libpamac-full.git"
cd "libpamac-full"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/snapd.git"
cd "snapd"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"


git clone "https://aur.archlinux.org/snapd-glib.git"
cd "snapd-glib"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/calamares.git"
cd "calamares"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/winboat.git"
cd "winboat"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/openboard.git"
cd "openboard"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/inputactions-kwin.git"
cd "inputactions-kwin"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/pamac-all.git"
cd "pamac-all"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

git clone "https://aur.archlinux.org/pamac-tray-icon-plasma.git"
cd "pamac-tray-icon-plasma"
makepkg -Sf --noconfirm
cd "$BUILD_DIR"

for pkg in "${PACKAGES[@]}"; do 
    echo -e "\e[1;92m |⚒️| ==== Baue Paket: $pkg... ==== |\e[0m"
    
    if [ ! -d "$pkg" ]; then
        echo "Klone $pkg von AUR..."
        git clone "https://aur.archlinux.org/$pkg.git" || { echo "❌ Fehler beim Klonen von $pkg"; exit 1; }
    fi
    
    cd "$BUILD_DIR/$pkg"

    # Paket bauen
    # -s installiert Abhängigkeiten, -r entfernt sie danach, -f erzwingt Neubau
    if ! makepkg -srfC --noconfirm; then
        echo -e "\e[1;91m ❌ FEHLER: Bau von $pkg fehlgeschlagen! \e[0m"
        exit 1
    fi

    # Prüfen, ob die .zst Datei existiert
    PKG_FILE=$(ls *.pkg.tar.zst 2>/dev/null | head -n 1)
    if [ -z "$PKG_FILE" ]; then
        echo -e "\e[1;91m ❌ KRITISCH: $pkg wurde gebaut, aber keine .pkg.tar.zst gefunden! \e[0m"
        exit 1
    fi

    echo "Kopiere $PKG_FILE nach $LOCAL_REPO..."
    cp "$PKG_FILE" "$LOCAL_REPO/"
    repo-add $LOCAL_REPO/custom.db.tar.gz $LOCAL_REPO/*.pkg.tar.zst
    sudo pacman -Syyu --noconfirm
done

echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"
echo -e "\e[1;92m |⚒️| Create custom database for local repository...|\e[0m"
echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"
repo-add $LOCAL_REPO/custom.db.tar.gz $LOCAL_REPO/*.pkg.tar.zst

sudo pacman -Syyu --noconfirm

check_and_update_repo

echo "SCRIPT_DIR: $SCRIPT_DIR"
cd "$SCRIPT_DIR"
echo -e "\e[1;92m |✅|=====================================================|\e[0m"
echo -e "\e[1;92m |✅| Local repo successfully created in $LOCAL_REPO      |\e[0m"
echo -e "\e[1;92m |✅|=====================================================|\e[0m"