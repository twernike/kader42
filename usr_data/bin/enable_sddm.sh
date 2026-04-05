# Pfad zur Systemd-Konfiguration im airootfs
airootfs="releng/airootfs"
systemd="$airootfs/etc/systemd"
system="$systemd/system"

# Install the package so that a symlink can be created. 
pacman -S sddm --noconfirm 

if [[ ! -d "$systemd" ]]; then
        mkdir -p "$systemd"
fi

if [[ ! -d "$system" ]]; then
        mkdir -p "$system"
fi

# display-manager.service Symlink setzen (entspricht systemctl enable sddm)
ln -sf /usr/lib/systemd/system/sddm.service \
       "$system/display-manager.service"