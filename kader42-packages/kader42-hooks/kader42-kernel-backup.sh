#!/bin/bash
# Get the version of the currently running stable kernel
KERNEL_VER=$(uname -r)
BACKUP_DIR="/boot/kader42-fallback"

echo "[kader42-kernel-backup] Delete the old backup and create a new fallback..." | systemd-cat -t kader42-installer
# 1. Thoroughly delete old backups to keep the EFI partition clean
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/modules"

# 2. Boot-Dateien statisch sichern (ohne Versionsnummer im Dateinamen!)
cp /boot/vmlinuz-linux "$BACKUP_DIR/vmlinuz-linux"
cp /boot/initramfs-linux.img "$BACKUP_DIR/initramfs-linux.img"
[ -f /boot/intel-ucode.img ] && cp /boot/intel-ucode.img "$BACKUP_DIR/intel-ucode.img"

# 3. Back up kernel modules
# (Here, we MUST keep the version in the path so that, during a rollback, 
# they end up in the correct /usr/lib/modules/VERSION folder again)
# Important: Since we are staying on the root partition, we will use a directory outside of /boot
MODULES_BACKUP_DIR="/usr/share/kader42/modules-fallback"
mkdir -p "$MODULES_BACKUP_DIR/modules/${KERNEL_VER}"

rsync -a --delete "/usr/lib/modules/${KERNEL_VER}/" "$MODULES_BACKUP_DIR/modules/${KERNEL_VER}/"

# 4. Create a static systemd boot entry (this will simply be overwritten with every update)
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
MODULES_BACKUP_DIR="/usr/share/kader42/modules-fallback"
mkdir -p "$MODULES_BACKUP_DIR/modules/${KERNEL_VER}"

rsync -a --delete "/usr/lib/modules/${KERNEL_VER}/" "$MODULES_BACKUP_DIR/modules/${KERNEL_VER}/"

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
exit 0