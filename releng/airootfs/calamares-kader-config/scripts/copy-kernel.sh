#!/bin/bash


# 1. Den Namen des einzigen Ordners in /usr/lib/modules finden
# Wir nehmen den ersten Treffer, falls mehrere da sind
KERNEL_DIR=$(find /usr/lib/modules -maxdepth 1 -mindepth 1 -type d -printf '%P\n' | head -n 1)
presetSrcDir="/usr/share/calamares/linux-preset"
presetDestDir="/etc/mkinitcpio.d"

echo
echo "***************************************************************"
echo "STEP: copy-kernel"
echo "Kernel-Directory in /usr/lib/modules: $KERNEL_DIR"
echo "linux.preset source directory:        $presetSrcDir"
echo "linux.preset dest directory:          $presetDestDir"
echo "***************************************************************"
echo

if [ -z "$KERNEL_DIR" ]; then
    echo "[copy-kernel] ERROR: No kernel folder found in /usr/lib/modules!"
    exit 1
fi

echo "Found kernel version: $KERNEL_DIR"

# 2. Verzeichnisse sicherstellen & Kopieren
mkdir -p /boot
mkdir -p "$presetDestDir"

# 2. Kopieren mit vollem, absolutem Pfad
echo "[copy-kernel] Copying kernel and preset..."
cp "/usr/lib/modules/$KERNEL_DIR/vmlinuz" /boot/vmlinuz-linux

presetSrc="$presetSrcDir/linux.preset"

if [ -f "$presetSrc" ]; then
    cp "$presetSrc" "$presetDestDir/linux.preset"
    echo "[copy-kernel] Success: Preset copied from etc_temp."
else
    echo "[copy-kernel] ERROR: Preset source not found at $presetSrc! Cannot copy it!"
    exit 1
fi

# 3. Validierung (dein Teil)
if [ -f /boot/vmlinuz-linux ]; then
    echo "[copy-kernel] Success: Kernel copied to /boot."
else
    echo "[copy-kernel] ERROR: Copy failed!"
    exit 1
fi