#!/bin/bash
# Configuration
shareCalamares="/usr/share/calamares"
modules="$shareCalamares/modules"
branding="$shareCalamares/branding"
qmlCalamares="$shareCalamares/qml"
linuxPreset="$shareCalamares/linux-preset"
calamaresScripts="$shareCalamares/scripts"
tmpCalamares="/calamares-kader-config"
tmpUsrLib="$tmpCalamares/usr_lib"
tmpLinuxPreset="$tmpCalamares/linux-preset"
tmpLibModules="$tmpUsrLib/modules"
tmpBootloaderLib="$tmpLibModules/bootloader"
tmpOneShotPreparer="$tmpLibModules/oneshot-preparer"
usrLib="/usr/lib"
usrLibCalamares="$usrLib/calamares"
usrModules="$usrLibCalamares/modules"
bootloaderLib="$usrModules/bootloader"
oneShotPreparerLib="$usrModules/oneshot-preparer"
tmp_preset="/preset_tmp"
presetDir="/etc/mkinitcpio.d"


echo -e "\e[1;92m ██████████████████████████████████████████████████████████████████████████████████████████████████
 █████████████████████████████▓░░░▓██████████████████████████████▒░░░▓█████████████████████████████
 ███████████████████████████▓░░███░ ▒██████████████████████████▒ ░▓ █░░▓███████████████████████████
 ███████████████████████████░ ░░ ░░░░██████████████████████████░░░░  ░ ░███████████████████████████
 ████████████████████████████▓░░░ █▒████████████████████████████░▓░░░ ░████████████████████████████
 ████████████████████████████████  ███████░░░░ ░ ░░ ░░ ░░░▒▒████▓░░████████████████████████████████
 ████████████████████████████████░ ░   ░░░▓▓▓▓▒▒▓▓▓▓▒▒▒▓▓█▒░░░ ░ ░▒████████████████████████████████
 ████████████████████████████▒░ ░▓▓█░ ░░░ ░   ░░    ░ ░ ░ ░░░░ ░█▓▓  ░▒████████████████████████████
 █████████████████████████░░░░▓▒▓▒▓░▓░ ▓░░░░   ░    ░ ░░   ░▓░ ▓░▓▒▓▒▓░ ░▒█████████████████████████
 ███████████████████████▓ ░▓▒░      ░▓ ░▓▒▒▒░░░▒▒▓▓▓▒▒░░▒▒░▓░░▓░░░░   ░▒▓ ░████████████████████████
 ██████████████████████▒ ░▓ ▒  ░   ░  ▓█░░▒▓█▓▓▓▓▓▓▓▓▓▓█▓▒░░█▓░ ░░░  ░░▒░▓░ ▒██████████████████████
 ███████████████████▒    ▓   ░░░░        ░░     ░   ░░ ░  ░ ░   ░░░    ░░ ▓    ▒███████████████████
 ████████████████▒ ░▓▓▓▓ ▓ ░░   ░ ░▒▒▒░░░░░░     ░     ░     ░▒▒▒░  ░ ░   ▓░▒▒▓▓ ░▓████████████████
 ███████████████░░▓▓░▓▓▓ ▒     ░▓▒░▓▓░░▒▓▓░   ░░    ░ ░░ ░▓▓░ ░▓▓░▒▓░   ░░▒ ▓▓▓░▒▓ ░███████████████
 ██████████████░ ▒░▓░░▓░ ▒▓ ░░▓▓▓░░▓▒  ░▓▓▓░░   ░ ░░░ ░ ░▓▓▒░  ▓▓░░▒▓▓ ░ ▒▒░▒▓░░▓░▒░░██████████████
 █████████████  █░ ▓▒░▓ ░░▓ ░░▓░▓▓▓▓▓▓▓▓▒▓▓▓  ░ ░░░░░░░ ▓▓▒▒▓▓▓▓▓▓▓▓░▓▒░░▓░░ ▒░▒▓░░█ ██████████████
 ██████████████░▒░ ▓▓░▓  ░▓░ ░▓░▓░▓▓▓▓▓▓▓▓░▓ ░  ░  ░░  ░▓░▓▓▓▓▓▓▓▓░▓░▓▒  ▓░ ░▓ ▒▒ ░▒ ██████████████
 ██████████████▒░▓░▓▓ ▓   ▓░░░▓▓░▒ ░█▓▓░░░▓▒   ░░    ░  ▒▓▒░░▓▓█░ ▒░▓▓░ ░▓   ▓░▒▓░▓░▒██████████████
 ███████████████▒ ░▓▒ ▓▒▒░▒░   ▒▓▒░░░ ░ ▒▓░     ░░░ ░ ░  ░▓▒░  ░░░▒▓▒   ░▓ ▒▒▓░▒▓░ ▒███████████████
 █████████████████▓░░░▓░░░░▓  ░ ░░░▓▒▒▓░ ░░░ ░▓█░░░░▓▓░ ░  ░░▓▒▒▓░░    ░▓░░░░▓░░░▓█████████████████
 ████████████████████▓░    ▒▒▓  ░ ░░ ░ ░   ░░░░  ░    ░░  ░   ░ ░░░ ░ ▒▒▒    ░▒████████████████████
 █████████████████████████░ ░▓░░   ░   ░ ░░░   ░░░░░  ░░░░      ░░░░░░▓░ ░█████████████████████████
 ███████████████████████████░ ░▓▓░ ░░░ ░  ░ ░░░    ░░░ ░     ░░░ ░░▓▓░ ░▒██████████████████████████
 █████████████████████████████▒░░░ ▒▓▓█░░░░░   ░░ ░ ░░    ░░░█▓▓▒░░░░██████████████████████████████
 ██████████████████████████████████░▒ ░░░░░░░░░▒░░░░░░░░ ░░░░░░▒░██████████████████████████████████
 ███████████████████████████████████████████████ ░░ ███████████████████████████████████████████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████\e[0m"

echo -e "\x1b[43m\e[1;31m                                           \e[0m"
echo -e "\x1b[43m\e[1;31m ######################################### \e[0m"
echo -e "\x1b[43m\e[1;31m # 🚀 Start script customize_airootfs.sh # \e[0m"
echo -e "\x1b[43m\e[1;31m ######################################### \e[0m"
echo -e "\x1b[43m\e[1;31m                                           \e[0m"

echo
echo -e "\x1b[38;1;208m |=====================================================| \e[0m"
echo -e "\x1b[38;1;208m | 🔑 | [customize_airootfs] Set a clean XDG directory | \e[0m"
echo -e "\x1b[38;1;208m |=====================================================| \e[0m"

sed -i 's|#TMPDIR="/tmp"|TMPDIR="/var/tmp"|' /etc/mkinitcpio.conf

echo
echo -e "\x1b[38;1;208m |=======================================================| \e[0m"
echo -e "\x1b[38;1;208m | 🔑 | [customize_airootfs] Execute create-live-user.sh | \e[0m"
echo -e "\x1b[38;1;208m |=======================================================| \e[0m"
echo

echo -e  "\x1b[43m\e[38;5;20m ##############################################################################\e[0m"
echo -e  "\x1b[43m\e[38;5;20m # ✍🏼 | [customize_airootfs] Set ownership of system directories to root:root #\e[0m"
echo -e  "\x1b[43m\e[38;5;20m # ✍🏼 | [customize_airootfs] and set read/write/execute permissions           # \e[0m"
echo -e  "\x1b[43m\e[38;5;20m ##############################################################################\e[0m"
echo 

# chmod 755 /home/liveuser/* || true
# chmod +x /home/liveuser/* || true

chmod 777 /etc/skel/.config/autostart/* || true
chmod +x /etc/skel/.config/autostart/* || true

chmod 644 /etc/systemd/system/*.service || true
chmod 644 /etc/systemd/user/*.service || true

chmod 0644 /etc/sudo.conf
chmod 0644 /etc/sudoers
# chmod 777 /home/liveuser/Desktop/calamares.desktop

echo -e "\x1b[43m\e[38;5;20m 🧹 clean up calamares directories \e[0m"
rm -rf $shareCalamares

echo -e "\x1b[38;5;208m ################################################################## \e[0m"
echo -e "\x1b[38;5;208m # ✍🏼| [customize_airootfs] create needed calamares directories...#\e[0m"
echo -e "\x1b[38;5;208m ################################################################## \e[0m"
echo

mkdir -p "$shareCalamares"
mkdir -p "$modules"
mkdir -p "$branding"
mkdir -p "$qmlCalamares"
mkdir -p "$calamaresScripts"
mkdir -p "$usrLibCalamares"
mkdir -p "$usrModules"
mkdir -p "$bootloaderLib"
mkdir -p "$oneShotPreparerLib"

echo -e "\x1b[95m\e[1;96m ################################################################################################# \e[0m"
echo -e "\x1b[95m\e[1;96m # 🗐 | [customize_airootfs] Copy the calamares configuration files to the needed directories... # \e[0m"
echo -e "\x1b[95m\e[1;96m ################################################################################################\e[0m"

cp -r $tmpCalamares/modules/. $modules
cp -r $tmpCalamares/branding/. $branding
cp -r $tmpCalamares/qml/. $qmlCalamares
cp -r $tmpCalamares/scripts/. $calamaresScripts
cp -r $tmpCalamares/settings.conf /usr/share/calamares
cp -R $tmpLinuxPreset $shareCalamares
cp -r $tmpOneShotPreparer/* $oneShotPreparerLib

chmod +x $calamaresScripts/*.sh

echo -e "\x1b[43m\e[38;5;20m ####################################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # ⚙️ | [customize_airootfs] Enable needed services # \e[0m"
echo -e "\x1b[43m\e[38;5;20m ####################################################\e[0m"

# Activate services
systemctl enable iio-sensor-proxy.service
systemctl enable bluetooth.service
systemctl --user enable --now kader42-tablet-event-listener.service

echo -e "\x1b[43m\e[38;5;20m ####################################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # ⚙️ | [customize_airootfs] Reindex HWDB...        # \e[0m"
echo -e "\x1b[43m\e[38;5;20m ####################################################\e[0m"

# Reindex HWDB (IMPORTANT for rotation!)
systemd-hwdb update
udevadm trigger

echo
echo -e "\x1b[43m\e[38;5;20m ########################################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # ⚙️ [customize_airootfs] Enforce systemd presets now! #\e[0m"
echo -e "\x1b[43m\e[38;5;20m ########################################################\e[0m"
systemctl preset-all
echo

pacman -Sy
echo -e "\x1b[43m\e[38;5;20m ###########################################################################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # ⚙️ | [customize_airootfs] Builds the graphical database for the Kader⁴² software center #\e[0m"
echo -e "\x1b[43m\e[38;5;20m ###########################################################################################\e[0m"
echo 

appstreamcli refresh-cache --force  # 
mkdir -p /usr/lib/systemd/user/default.target.wants/

ln -sf /usr/lib/systemd/user/kader42-tablet-event-listener.service \
       /usr/lib/systemd/user/default.target.wants/kader42-tablet-event-listener.service

echo 'polkit.addAdminRule(function(action, subject) {
    return ["unix-group:wheel"];
});' | sudo tee /etc/polkit-1/rules.d/49-wheel-group.rules


if id plasmalogin &>/dev/null; then
    usermod -aG video,render plasmalogin
fi

echo -e "\x1b[43m\e[38;5;20m ##################################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # 📁 [customize_airootfs] Add missing XDG folder #\e[0m"
echo -e "\x1b[43m\e[38;5;20m ##################################################\e[0m"
echo
su - liveuser -c "xdg-user-dirs-update"

mkdir -p /home/liveuser
cp -aT /etc/skel/ /home/liveuser/
chown -R 1000:1000 /home/liveuser 

echo -e "\x1b[43m\e[38;5;20m ########################################\e[0m"
echo -e "\x1b[43m\e[38;5;20m # ℹ️ Add OS release info to /usr/lib...#\e[0m"
echo -e "\x1b[43m\e[38;5;20m ########################################\e[0m"
echo 

cp /os-release-info/os-release /usr/lib

echo -e "\x1b[43m\e[38;5;20m ##################################################################e[0m"
echo -e "\x1b[43m\e[38;5;20m # 🖊 Create symlink for /usr/lib/os-release to /etc/os-release...#\e[0m"
echo -e "\x1b[43m\e[38;5;20m ##################################################################e[0m"
echo
ln -sf /usr/lib/os-release /etc/os-release

echo "Refresh icon cache..."
gtk-update-icon-cache -f /usr/share/icons/hicolor
gtk-update-icon-cache -f /usr/share/icons/Kader42

echo
echo -e "\x1b[44m\e[1;118m  ##################################\e[0m"
echo -e "\x1b[44m\e[1;118m  # customize_airootfs.sh DONE! ✅️ #\e[0m"
echo -e "\x1b[44m\e[1;118m  ##################################\e[0m"