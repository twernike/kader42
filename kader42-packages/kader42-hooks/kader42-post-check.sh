#!/bin/bash
# Wenn mkinitcpio fehlerhaft war oder pacman abgebrochen ist (prüfbar über Exit-Codes oder Existenz des Images)
if [ ! -s /boot/initramfs-linux.img ] || [ -f /var/lib/pacman/db.lck ]; then
    echo "⚠️ Update failed! Set the rollback flag for the next boot..."
    touch /boot/kader42-rollback.trigger
fi