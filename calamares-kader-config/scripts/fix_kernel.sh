#!/bin/bash
# fix_kernel.sh - Kader42 Framework 12 Edition

# Funktion für schöneres Logging in Calamares
log() {
    echo "[KADER⁴²-INSTALLER]  $1"
}

log "Start kernel repair and hardware optimization..."

# 1. NETWORK & DNS
log "Configure DNS..."
echo "nameserver 1.1.1.1" > /etc/resolv.conf

# 2. WRITE MIRRORLIST
log "Set Mirrorlist to RWTH Aachen..."
echo "Server = http://ftp.halifax.rwth-aachen.de/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

# 3. REPAIR KEYRING
log "Update keyring for pacman..."
pacman-key --init
pacman-key --populate archlinux
pacman -Sy --noconfirm archlinux-keyring

# 4. UPDATE KERNEL & HARDWARE STUFF
log "Install kernel, firmware, and microcode..."
pacman -S --noconfirm linux linux-firmware intel-ucode

# 5. MKINITCPIO CONFIGURATION
log "Optimize mkinitcpio for Framework (i915, iwlwifi, plymouth)..."
sed -i 's/^MODULES=([^)]*)/MODULES=(i915 iwlwifi)/' /etc/mkinitcpio.conf
sed -i 's/^HOOKS=([^)]*)/HOOKS=(base udev microcode modconf block keyboard keymap plymouth filesystems fsck)/' /etc/mkinitcpio.conf


# 6. BUILDING INITRAMFS
log "Generating initramfs (this may take a moment)..."
if mkinitcpio -p linux; then
    log "Initramfs successfully created."
else
    log "ERROR: mkinitcpio failed!"
    exit 1
fi

log "Configure plymouth..."
plymouth-set-default-theme kader42

# 7. OPTIONALE PAKETE
# über postinstall-Script

# /etc/kader42/optional_packages.conf erstellen
mkdir -p /etc/kader42

PACKAGE_IDS=("google-chrome" "visual-studio-code-bin" "heroic-games-launcher-bin" "waydroid-git" "waydroid-helper" "waydroid-launcher-git" "spotify")
ARGUMENTS=("$@")  # Aus Calamares optional selection

for i in "${!PACKAGE_IDS[@]}"; do
    if [[ "${ARGUMENTS[i]}" == "t" ]]; then
        echo "${PACKAGE_IDS[i]}=t" >> /etc/kader42/optional_packages.conf
    else
        echo "${PACKAGE_IDS[i]}=f" >> /etc/kader42/optional_packages.conf
    fi
done


cat <<'EOF' > /etc/systemd/system/kader42-welcome.service
[Unit]
Description=Kader42 Welcome - install optional packages
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/kader42-welcome.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

systemctl enable kader42-welcome.service

log "Kernel installation complete."
log "Optional packages will be installed after first login"
log "Ready for bootloader installation."
exit 0