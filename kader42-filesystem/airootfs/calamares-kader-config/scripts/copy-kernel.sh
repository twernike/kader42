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

MAX_RETRIES=5
SLEEP_TIME=2

# Warte kurz oder prüfe auf Mount

echo "[copy-kernel] Waiting for /boot to mount..."

# Schleife für die Überprüfung
for i in $(seq 1 $MAX_RETRIES); do
    if mountpoint -q /boot; then
        echo "[copy-kernel] Success: /boot is mounted."
        break
    else
        echo "[copy-kernel] Attempt $i/$MAX_RETRIES: /boot is not yet a mount point. Waiting $SLEEP_TIME seconds..."
        sleep $SLEEP_TIME
    fi

    # Wenn der letzte Versuch auch fehlschlägt
    if [ $i -eq $MAX_RETRIES ]; then
        echo "[copy-kernel] ERROR: /boot is still not ready after $MAX_RETRIES attempts!"
        exit 1
    fi
done

if [ -z "$KERNEL_DIR" ]; then
    echo "[copy-kernel] ERROR: No kernel folder found in /usr/lib/modules!"
    exit 1
fi

echo "[copy-kernel] Found kernel version: $KERNEL_DIR"

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