#!/bin/bash

BUILD_DIR="build"
LOCAL_PACKAGES="/packages"
LOCAL_REPO="$LOCAL_PACKAGES/custom"

PACKAGES=(
    #"python-libinput"
    # "inputactions-kwin"
    # "plasma-mobile"
    # "ruby-fusuma"
    # "ruby-fusuma-plugin-appmatcher"
    # "ruby-fusuma-plugin-keypress"
    # "ruby-fusuma-plugin-remap"
    # "ruby-fusuma-plugin-sendkey"
    # "ruby-fusuma-plugin-tap"
    # "ruby-fusuma-plugin-thumbsense"
    # "ruby-fusuma-plugin-wmctrl"
    # "calamares-git"
    # "yay"
    # "scrivano"
    # "winboat"
    # "heroic-games-launcher-bin"
    # "heroic-gogdl"
    # "openboard"
    # "libpamac-aur"
    # "libnotify"
    # "libpamac"
    # "qt6-base"
    # "knotifications"
    # "kstatusnotifieritem"
    # "pamac-aur"
    # "pamac-tray-icon-plasma"
    )
cd "$BUILD_DIR"

for pkg in "${PACKAGES[@]}"; do 
     echo -e "\e[1;92m |⚒️| ==== Build package $pkg... ==== |\e[0m"
    # # Paket von AUR klonen (aurgit oder git)
    if [ ! -d "$pkg" ]; then
        git clone "https://aur.archlinux.org/$pkg.git"
    fi
    cd "$pkg"
    # build package without installation
    makepkg -srf --noconfirm
    # copy built package to local repo
    cp *.pkg.tar.zst "$LOCAL_REPO"
done

echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"
echo -e "\e[1;92m |⚒️| Create custom database for local repository...|\e[0m"
echo -e "\e[1;92m |⚒️| ============================================= |\e[0m"

repo-add $LOCAL_REPO/custom.db.tar.gz $LOCAL_REPO/*.pkg.tar.zst

echo -e "\e[1;92m |✅|=====================================================|\e[0m"
echo -e "\e[1;92m |✅| Local repo successfully created in $LOCAL_REPO      |\e[0m"
echo -e "\e[1;92m |✅|=====================================================|\e[0m"