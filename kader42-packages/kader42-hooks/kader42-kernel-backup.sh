#!/bin/bash
KERNEL_VER=$(uname -r)
BACKUP_DIR="/boot/kader42-fallback"

echo "[kader42-kernel-backup] Update the fallback system..." | systemd-cat -t kader42-installer

# Clean up old backups
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/modules/${KERNEL_VER}"

# Back up boot files (Here we use the actual files from /boot)
cp /boot/vmlinuz-linux "$BACKUP_DIR/vmlinuz-linux"
cp /boot/initramfs-linux.img "$BACKUP_DIR/initramfs-linux.img"
[ -f /boot/intel-ucode.img ] && cp /boot/intel-ucode.img "$BACKUP_DIR/intel-ucode.img"

if [ -d "/usr/lib/modules/${KERNEL_VER}" ]; then
    cp -a "/usr/lib/modules/${KERNEL_VER}/." "$BACKUP_DIR/modules/${KERNEL_VER}/"
fi

# Create a static systemd-boot entry
# Dynamically detect the NVMe root partition
ROOT_DEV=$(findmnt -n -o SOURCE /)
ROOT_UUID=$(blkid -s UUID -o value "$ROOT_DEV")

cat << EOF > /boot/loader/entries/kader42-fallback.conf
title   Kader4² (Fallback zu $KERNEL_VER)
linux   /kader42-fallback/vmlinuz-linux
initrd  /kader42-fallback/intel-ucode.img
initrd  /kader42-fallback/initramfs-linux.img
options root=UUID=${ROOT_UUID} rw log_level=3
EOF

echo "[kader42-kernel-backup] Fallback system successfully created." | systemd-cat -t kader42-installer
exit 0