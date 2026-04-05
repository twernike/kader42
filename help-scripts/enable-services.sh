#!/bin/bash
# ArchISO Service Setup Script
# For: KDE Plasma + SDDM + iio-sensor-proxy

echo -e "\x1b[43m\e[38;5;20m######################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m#  Start script enable-services.sh   #\e[0m"
echo -e "\x1b[43m\e[38;5;20m######################################\e[0m"

releng="releng"
AIROOTFS="$releng/airootfs"
SYSD="$AIROOTFS/etc/systemd/system"

echo -e "==> \x1b[43m\e[38;5;20m Create needed system folders under /etc/systemd…\e[0m"
mkdir -p "$SYSD"
mkdir -p "$SYSD/graphical.target.wants"
mkdir -p "$SYSD/multi-user.target.wants"

# echo -e "==> \x1b[43m\e[38;5;20m Activate network……\e[0m"

# ln -sf /usr/lib/systemd/system/systemd-networkd.service \
#     "$SYSD/multi-user.target.wants/systemd-networkd.service"

# systemctl systemd-networkd.service => ist enabled
# Fehler ==> Failed to start Network Configuration
# networkctl status  => Connection refused
# Im Ordner network ist keine Konfigurationsdatei

# Umstellen auf Networkmanager?

# echo -e "==> \x1b[43m\e[38;5;20m Create symlink for liveuser service……\e[0m"
# ln -sf ../../usr/lib/systemd/system/livecd-user.service \
#     releng/airootfs/etc/systemd/system/multi-user.target.wants/livecd-user.service

echo -e "==> \x1b[43m\e[38;5;20m Activate iio-sensor-proxy……\e[0m"
ln -sf /usr/lib/systemd/system/iio-sensor-proxy.service \
    "$SYSD/multi-user.target.wants/iio-sensor-proxy.service"

# echo -e "==> \x1b[43m\e[38;5;20m (Optional) Activate important default services\e[0m"
# echo -e "==> \x1b[43m\e[38;5;20m Activate time zone service...\e[0m"

# ln -sf /usr/lib/systemd/system/systemd-timesyncd.service \
#     "$SYSD/multi-user.target.wants/systemd-timesyncd.service"

ln -sf /usr/lib/systemd/system/sddm.service \
    "$SYSD/display-manager.service"

# Activation for graphical.target
ln -sf ../display-manager.service \
    "$SYSD/graphical.target.wants/display-manager.service"

echo -e "✅️  \x1b[43m\e[38;5;20m Done! Systemd services are correctly enabled for ArchISO.\e[0m"
