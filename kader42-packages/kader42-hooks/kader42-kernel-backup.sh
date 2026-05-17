#!/bin/bash
# Hole die Version des aktuell laufenden, stabilen Kernels
KERNEL_VER=$(uname -r)
BACKUP_DIR="/boot/kader42-fallback"

echo "[kader42-kernel-backup] Delete the old backup and create a new fallback..." | systemd-cat -t kader42-installer
# 1. Altes Backup rigoros löschen, um die EFI-Partition sauber zu halten
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/modules"

# 2. Boot-Dateien statisch sichern (ohne Versionsnummer im Dateinamen!)
cp /boot/vmlinuz-linux "$BACKUP_DIR/vmlinuz-linux"
cp /boot/initramfs-linux.img "$BACKUP_DIR/initramfs-linux.img"
[ -f /boot/intel-ucode.img ] && cp /boot/intel-ucode.img "$BACKUP_DIR/intel-ucode.img"

# 3. Kernel-Module sichern
# (Hier MÜSSEN wir die Version im Pfad behalten, damit sie beim Rollback 
# wieder im richtigen /usr/lib/modules/VERSION Ordner landen)
rsync -a "/usr/lib/modules/${KERNEL_VER}/" "$BACKUP_DIR/modules/${KERNEL_VER}/"

# 4. Statischen systemd-boot Eintrag schreiben (wird bei jedem Update einfach überschrieben)
ROOT_UUID=$(blkid -s UUID -o value /dev/nvme0n1p2)

cat << EOF > /boot/loader/entries/kader42-fallback.conf
title   Kader4² (Fallback to $KERNEL_VER)
linux   /kader42-fallback/vmlinuz-linux
initrd  /kader42-fallback/intel-ucode.img
initrd  /kader42-fallback/initramfs-linux.img
options root=UUID=${ROOT_UUID} rw log_level=3
EOF

echo "[kader42-kernel-backup] The fallback system has been successfully updated." | systemd-cat -t kader42-installer
exit 0