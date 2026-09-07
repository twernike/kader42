#!/bin/bash
# /usr/local/bin/install_optional_packages.sh

TARGET=/mnt
PACKAGES=""

# Array der Paket-IDs (Muss in der GLEICHEN Reihenfolge wie in shellprocess_optional.conf sein!)
# Die IDs sind die Paketnamen.
PACKAGE_IDS=(
    "google-chrome"
    "visual-studio-code-bin"
    "heroic-games-launcher-bin"
    "waydroid-git"
    "waydroid-helper"
    "waydroid-launcher-git"
    "spotify"
)

# Das Array der übergebenen Argumente ($1, $2, $3, ...)
ARGUMENTS=("$@") 
# Das "@" erfasst alle an das Skript übergebenen Argumente ($1 bis $6)

# Durchlaufe die Liste der möglichen Pakete
for i in "${!PACKAGE_IDS[@]}"; do
    # Prüfe den Status (t oder f) des zugehörigen Arguments
    # ${ARGUMENTS[i]} ist der Status (t/f), ${PACKAGE_IDS[i]} ist der Name
    if [ "${ARGUMENTS[i]}" == "t" ]; then
        PACKAGES="$PACKAGES ${PACKAGE_IDS[i]}"
    fi
done

# Entferne führendes Leerzeichen (optional, aber sauber)
PACKAGES=$(echo $PACKAGES | sed 's/^ //')

# 3. Ausführung des Jobs im Chroot
if [ -n "$PACKAGES" ]; then
  arch-chroot "$TARGET" /bin/bash -c "
    
    echo 'Update pacman database and install basic build tools...'
    pacman -Syu --noconfirm git base-devel

    echo 'Start yay installation of the following AUR packages: $PACKAGES'
    
    yay -S --noconfirm $PACKAGES
  "
fi

exit 0