# Pfad zur Systemd-Konfiguration im airootfs
airootfs="releng/airootfs"
systemd="$airootfs/etc/systemd"
system="$systemd/system"
multiusertarget="$system/multi-user.target.wants"

# Install the package so that a symlink can be created. 
pacman -S iio-sensor-proxy --noconfirm 

if [[ ! -d "$systemd" ]]; then
        mkdir -p "$systemd"
fi

if [[ ! -d "$system" ]]; then
        mkdir -p "$system"
fi

if [[ ! -d "$multiusertarget" ]]; then
        mkdir -p "$multiusertarget"
fi

# Symlink anlegen
ln -sf /usr/lib/systemd/system/iio-sensor-proxy.service \
       "$airootfs/etc/systemd/system/multi-user.target.wants/iio-sensor-proxy.service"