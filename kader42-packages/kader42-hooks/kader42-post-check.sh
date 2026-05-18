#!/bin/bash
# /usr/share/kader42/kader42-post-check.sh

# 1. Retrieve the target version from the Pacman database
# On Arch, this returns the following format by default: “7.0.8.arch1-1”
PKG_VERSION=$(pacman -Q linux | awk '{print $2}')

# 2. Extract the actual version from the kernel configuration file
# Returns the following format in the kernel: “7.0.8-arch1-1”
if [ -f /boot/vmlinuz-linux ]; then
    FILE_VERSION=$(file -b /boot/vmlinuz-linux | grep -oP 'version \K[0-9]+\.[0-9]+\.[0-9]+-[a-zA-Z0-9.-]+')
else
    FILE_VERSION="missing"
fi

# 3. Sicherheitsnetz: Wenn das Initramfs fehlt oder leer ist, ist es sowieso ein Fehlschlag
if [ ! -s /boot/initramfs-linux.img ]; then
    FILE_VERSION="corrupt"
fi

# 4. The key: Normalization for the perfect string comparison
# Since Arch uses a period (“.arch”) in the package name but 
# a hyphen (“-arch”) in the kernel itself, we simply remove all periods and hyphens.
# “7.0.8.arch1-1” and “7.0.8-arch1-1” both become “708arch11”
NORM_PKG=$(echo "$PKG_VERSION" | tr -d '.-')
NORM_FILE=$(echo "$FILE_VERSION" | tr -d '.-')

# 5. The Real Version Comparison
if [ "$NORM_PKG" != "$NORM_FILE" ]; then
    echo "========================================================================="
    echo "⚠️  CRITICAL UPDATE ERROR DETECTED!"
    echo "   The kernel file on the disk ($FILE_VERSION) does not match"
    echo "   the installed package version ($PKG_VERSION)!"
    echo "========================================================================="
    echo "[Kader⁴² Post Check] Set the rollback flag for the next boot..."
    touch /boot/kader42-rollback.trigger
else
    echo "✅ [Kader⁴² Post Check] Integrity check successful."
    rm -f /boot/kader42-rollback.trigger
fi