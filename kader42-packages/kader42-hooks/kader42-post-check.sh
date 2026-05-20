#!/bin/bash
# /usr/share/kader42/kader42-post-check.sh

# 1. Retrieve the target version from the Pacman database
PKG_VERSION=$(pacman -Q linux | awk '{print $2}')

# 2. Extract the actual version from the kernel file
if [ -f /boot/vmlinuz-linux ]; then
    FILE_VERSION=$(file -b /boot/vmlinuz-linux | grep -oP 'version \K[0-9]+\.[0-9]+\.[0-9]+-[a-zA-Z0-9.-]+')
else
    echo "⚠️  [Kader⁴² Post Check] Couldn't determine the file version of the kernel image!"
    FILE_VERSION="missing"
fi

# 3. Fallback: If the initramfs is missing or empty, abort immediately
if [ ! -s /boot/initramfs-linux.img ]; then
    echo "⚠️ [Kader⁴² Post Check] CRITICAL: initramfs-linux.img ist korrupt oder fehlt!"
    touch /boot/kader42-rollback.trigger
    exit 0
fi

if [ "$FILE_VERSION" != "missing" ] && [ "$FILE_VERSION" != "corrupt" ]; then
    MODULES_DIR="/usr/lib/modules/${FILE_VERSION}"
    
    if [ ! -d "$MODULES_DIR" ]; then
        echo "⚠️  [Kader⁴² Post Check] The module directory for version $FILE_VERSION is completely missing!"
        touch /boot/kader42-rollback.trigger
        exit 0

    elif [ ! -f "$MODULES_DIR/modules.dep" ] || [ ! -s "$MODULES_DIR/modules.dep" ]; then
        echo "⚠️  [Kader⁴² Post Check] Module dependencies (modules.dep) are corrupted or empty!"
        touch /boot/kader42-rollback.trigger
        exit 0
    else
        # Höchste installierte Modulversion ermitteln
        MODULES_VER=$(ls -1 /usr/lib/modules/ | sort -V | tail -n 1)
        echo "[Kader⁴² Post Check] The kernel modules version is $MODULES_VER"    
    fi

    # 4. Normalization for the perfect three-way string comparison
    NORM_PKG=$(echo "$PKG_VERSION" | tr -d '.-')
    NORM_FILE=$(echo "$FILE_VERSION" | tr -d '.-')
    NORM_MODULE=$(echo "$MODULES_VER" | tr -d '.-')

    # 5.  The Real Three-Way Version Comparison
    # Bash-Syntax korrigiert: Entweder mit '||' zwischen zwei [ ] oder '-o' innerhalb von [ ]
    if [ "$NORM_PKG" != "$NORM_FILE" ] || [ "$NORM_FILE" != "$NORM_MODULE" ]; then
        echo "========================================================================="
        echo "⚠️  CRITICAL UPDATE ERROR DETECTED!"
        echo "   The versions on the system are asynchronous:"
        echo "   Pacman Package: $PKG_VERSION"
        echo "   Kernel Image:   $FILE_VERSION"
        echo "   Kernel Modules: $MODULES_VER"
        echo "========================================================================="
        echo "[Kader⁴² Post Check] Set the rollback flag for the next boot..."
        touch /boot/kader42-rollback.trigger
    else
        echo "✅ [Kader⁴² Post Check] Integrity check successful. All 3 stages match."
        rm -f /boot/kader42-rollback.trigger
    fi
fi