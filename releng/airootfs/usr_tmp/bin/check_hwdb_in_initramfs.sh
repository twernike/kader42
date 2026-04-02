#!/bin/bash
# check_hwdb_in_initramfs.sh
# With this script it is possible to check, if td

IMAGE_PATH="/boot/initramfs-linux.img" # Pfad zu deinem generierten Image

echo "🔍 Check Initramfs: $IMAGE_PATH"

# Liste den Inhalt des Images auf und suche nach der Datei
if lsinitcpio "$IMAGE_PATH" | grep -q "$1"; then
    echo "✅ Success: $1 found in image."
    
    # Extrahiere die Datei kurz, um den Inhalt zu prüfen (Vorsicht: Leerzeichen!)
    lsinitcpio -x "$IMAGE_PATH" "$1" -outdir /tmp/hwdb_check > /dev/null
    
    if grep -q "^ " "/tmp/hwdb_check/$1"; then
        echo "✅ Success: Indentation (space) found."
    else
        echo "❌ ERROR: The line ACCEL_MOUNT_MATRIX must start with a SPACE!"
    fi
    rm -rf /tmp/hwdb_check
else
    echo "❌ ERROR: $1 is missing in the image! Please check the FILES section in mkinitcpio.conf."
fi