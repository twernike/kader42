# Ein kleiner "Wachhund" am Ende der Installation
if [ ! -f /boot/EFI/systemd/systemd-bootx64.efi ] && [ ! -f /boot/EFI/BOOT/BOOTX64.EFI ]; then
    echo "ALERT: Bootloader was not installed!" >&2
    exit 1
fi