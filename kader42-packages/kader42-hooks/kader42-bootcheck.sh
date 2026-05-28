#!/bin/bash
# [Kader42-Bootcheck] Self-healing Pre-Update Boot Check

echo ":: [Kader42-Bootcheck] Run a storage safety check before updating..."

# Function for detecting and repairing the mount
ensure_boot_mounted() {
    # 1. Is /boot already mounted correctly as a VFAT partition?
    if mountpoint -q /boot; then
        local current_fs
        current_fs=$(findmnt -n -o FSTYPE /boot)
        if [ "$current_fs" = "vfat" ]; then
            return 0 # Everything's perfect; we can stop now.
        else
            echo "⚠️ [Kader42-Bootcheck]  /boot is mounted as ‘$current_fs’, not as vfat!" >&2
            return 1 # Incorrect file system (e.g., ghost folder is blocking access)
        fi
    fi

    # 2. If not mounted: Initiate self-healing
    echo "⚠️ [Kader42-Bootcheck] /boot is NOT mounted! Attempting automatic repair..."

    # Geister-Dateien im lokalen /boot-Ordner der Root-Partition prüfen
    # Wenn dort vmlinuz liegt, blockiert das potenziell oder verfälscht Updates
    if [ "$(ls -A /boot 2>/dev/null)" ]; then
        echo "⚠️ [Kader42-Bootcheck] Warning: Temporary files found in the unmounted /boot directory."
        echo ":: Clean up the local ghost folder for a clean mount point..."
        rm -rf /boot/*
    fi

    # Klassischen Mount über fstab versuchen
    echo ":: Try mounting /boot via /etc/fstab..."
    if mount /boot 2>/dev/null && mountpoint -q /boot; then
        echo "✅ [Kader42-Bootcheck] Self-healing successful: /boot mounted via fstab."
        return 0
    fi

    # Workaround: If fstab fails, we'll look for the EFI partition directly on the NVMe drive
    echo ":: fstab mount failed. Searching directly for an EFI partition..."
    local efi_dev
    efi_dev=$(blkid -o device -t TYPE=vfat | grep -E "nvme|sd" | head -n 1)

    if [ -n "$efi_dev" ]; then
        echo ":: EFI partition found on $efi_dev. Forcing mount to /boot..."
        if mount "$efi_dev" /boot 2>/dev/null; then
            echo "✅ [Kader42-Bootcheck] Self-healing successful: $efi_dev mounted directly to /boot."
            return 0
        fi
    fi

    return 1 # All attempts at repair have failed
}

# Performing self-healing
if ! ensure_boot_mounted; then
    echo "❌ [Kader42-Bootcheck] CRITICIAL ERROR: /boot could not be repaired!" >&2
    echo "   The kernel update is being aborted to prevent system damage." >&2
    exit 1
fi

# Final validity check (Does the folder structure exist?)
if [ ! -d "/boot/EFI" ] && [ ! -d "/boot/efi" ]; then
    echo "⚠️ [Kader42-Bootcheck] Note: /boot is formatted as vfat, but does not contain an ‘EFI’ folder."
fi

echo "✅ [Kader42-Bootcheck] /boot integrity verified. Update is being released."
exit 0