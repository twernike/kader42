#!/bin/bash
# check_hwdb_in_initramfs.sh

IMAGE_PATH="/boot/initramfs-linux.img" # Pfad zu deinem generierten Image
HWDB_FILE="etc/udev/hwdb.d/61-framework.hwdb"

echo "🔍 Check Initramfs: $IMAGE_PATH"

# Liste den Inhalt des Images auf und suche nach der Datei
if lsinitcpio "$IMAGE_PATH" | grep -q "$HWDB_FILE"; then
    echo "✅ Success: $HWDB_FILE found in image."
    
    # Extrahiere die Datei kurz, um den Inhalt zu prüfen (Vorsicht: Leerzeichen!)
    lsinitcpio -x "$IMAGE_PATH" "$HWDB_FILE" -outdir /tmp/hwdb_check > /dev/null
    
    if grep -q "^ " "/tmp/hwdb_check/$HWDB_FILE"; then
        echo "✅ Success: Indentation (space) found."
    else
        echo "❌ ERROR: The line ACCEL_MOUNT_MATRIX must start with a SPACE!"
    fi
    rm -rf /tmp/hwdb_check
else
    echo "❌ ERROR: $HWDB_FILE is missing in the image! Please check the FILES section in mkinitcpio.conf."
fi