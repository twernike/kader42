#!/bin/bash

BUILD_DIR="/build"
LOCAL_PACKAGES="/packages"
LOCAL_REPO="$LOCAL_PACKAGES/custom"
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

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
        echo -e "\e[1;91m |❌| Dependency $dep is not installed. Install the dependency...\e[0m"
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

PACKAGES=(
    "snapd"
    "snapd-glib"
    "inputactions-ctl"
    "pamac-cli"
    "asciidoc"
    "calamares-git"
    "yay"
    "libpamac-full"
    "winboat"
    "openboard"
    "inputactions-kwin"
    "pamac-all"
    "pamac-tray-icon-plasma"
    )

for pkg in "${PACKAGES[@]}"; do 
    echo -e "\e[1;92m |⚒️| ==== Build package $pkg... ==== |\e[0m"
    # # Paket von AUR klonen (aurgit oder git)
    if [ ! -d "$pkg" ]; then
        git clone "https://aur.archlinux.org/$pkg.git"
    fi
    cd "$BUILD_DIR/$pkg"
    # build package without installation
    makepkg -srf --noconfirm
    # copy built package to local repo
    cp *.pkg.tar.zst "$LOCAL_REPO"
    repo-add $LOCAL_REPO/custom.db.tar.gz $LOCAL_REPO/$pkg*.pkg.tar.zst
    sudo pacman -Syyu --noconfirm

done

echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"
echo -e "\e[1;92m |⚒️| Create custom database for local repository...|\e[0m"
echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"

repo-add $LOCAL_REPO/custom.db.tar.gz $LOCAL_REPO/*.pkg.tar.zst

cd "$SCRIPT_DIR"
echo -e "\e[1;92m |✅|=====================================================|\e[0m"
echo -e "\e[1;92m |✅| Local repo successfully created in $LOCAL_REPO      |\e[0m"
echo -e "\e[1;92m |✅|=====================================================|\e[0m"