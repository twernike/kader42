#!/bin/bash
# Configuration
shareCalamares="/usr/share/calamares"
modules="$shareCalamares/modules"
branding="$shareCalamares/branding"
qmlCalamares="$shareCalamares/qml"
calamaresScripts="$shareCalamares/scripts"
tmpCalamares="/calamares-kader-config"
tmpUsrLib="$tmpCalamares/usr_lib"
tmpLibModules="$tmpUsrLib/modules"
tmpBootloaderLib="$tmpLibModules/bootloader"
tmpOneShotPreparer="$tmpLibModules/oneshot-preparer"
tmpUsr="/usr_tmp"
usrLib="/usr/lib"
tmpEtc="/etc_tmp"
usrLibCalamares="$usrLib/calamares"
usrModules="$usrLibCalamares/modules"
bootloaderLib="$usrModules/bootloader"
oneShotPreparerLib="$usrModules/oneshot-preparer"
tmp_preset="/preset_tmp"
presetDir="/etc/mkinitcpio.d"
hwdbDir="/etc/udev/hwdb.d"
hwdFilename="61-framework.hwdb"
frameworkHwdb="$hwdbDir/$hwdFilename"



echo -e "\x1b[43m\e[1;31m                                                        \e[0m"
echo -e "\x1b[43m\e[1;31m ###################################################### \e[0m"
echo -e "\x1b[43m\e[1;31m # 🚀 Start script customize_airootfs.sh for building # \e[0m"
echo -e "\x1b[43m\e[1;31m ###################################################### \e[0m"
echo -e "\x1b[43m\e[1;31m                                                        \e[0m"

cat <<'EOF'                                                                                                                                              
##############################################################################################################################################
##############################################################################################################################################
##################################################################################.                                   +#######################
#########################################################################.          -+########################+.             #################
##################################################################.       -#############################################         +############
############################################################-     +##########################################################       ##########
#######################################################.   .#####################################################################     .#######
##################################################.  .#############################################################################     ######
#############################################+  #####################################################################################    #####
#########################################--#####################################################################   ####     ##########    ####
###############################################################################################################    ##         #########   -###
#################    +##########.    .##############################    .####################################.     ########   #########.   ###
#################    .#########     ################################    -###################################   #   #######   +#########   .###
#################    .#######     +#################################    -##################################   ##   #####    ###########   ####
#################    .#####      ###################################    -#################################           #    ############   .####
#################     ###.     ###########+     .############.    -#    .########     -#######++--####   #######   ##         #######-   #####
#################    .##     ##########             ######              .####+            ####    #-     #######   ##         ######.   ######
#################          +###########.   ####      ###+     -###-     .###     .###      ###           ##########################   -#######
#################         +######################    -##     #######    .##     #######     ##      #############################-   #########
#################           ################-.       .#     ########    .#-    ########+    ##     #############################   -##########
#################    .#+      ##########             .#     ########    .#                  ##    ############################   .############
##########-######    .###      +######      .####    .#     ########    .#                 .##    ##########################   .##############
######### #######    .#####      #####    #######    .#     ########    .##    ###############    #######################-   -################
#######  ########    .######+      ###    ######     .##     ######      ##     -#############    #####################    ###################
######  #########    .########      +#               .###                ###.              ###    ##################    .#####################
#####  ##########    .##########      #-        #.    ####         ##    #####.           ####    ###############     ########################
####+ -#######################################################################################################     ###########################
####  +####################################################################################################    .##############################
####  -################################################################################################     ##################################
####+  ############################################################################################     +#####################################
#####   ######################################################################################      +#########################################
######   +###############################################################################      -##############################################
#######+   -#######################################################################       -###################################################
#########+    +#############################################################+        #########################################################
############.     .#################################################+.        .###############################################################
################         -###############################+.            -######################################################################
#####################+                                       .+###############################################################################
##################################++-.....--++################################################################################################
##############################################################################################################################################                                                               
EOF

echo
echo -e "\x1b[38;5;208m |================================| \e[0m"
echo -e "\x1b[38;5;208m | 🔑 | Set a clean XDG directory | \e[0m"
echo -e "\x1b[38;5;208m |================================| \e[0m"
# XDG-Verzeichnis sauber setzen

sed -i 's|#TMPDIR="/tmp"|TMPDIR="/var/tmp"|' /etc/mkinitcpio.conf

mkdir -p /home/liveuser
chown -R liveuser:liveuser /home/liveuser
passwd -d liveuser

echo "liveuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser
chmod 440 /etc/sudoers.d/liveuser

echo -e "\e[1;92m Copy usr-Data...[0m"
cp -R "$tmpUsr/." /usr

touch /home/liveuser/.zshrc
chown liveuser:liveuser /home/liveuser/.zshrc

echo -e  "\x1b[43m\e[38;5;20m |=======================================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m | ✍🏼 | Set ownership of system directories to root:root |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |=======================================================|\e[0m"
echo 

chmod 755 /usr/bin/* || true
chmod +x /usr/bin/* || true

chmod 755 /usr/local/bin/* || true
chmod +x /usr/local/bin/* || true

chmod 755 /home/liveuser/*.sh || true
chmod +x /home/liveuser/*.sh || true

chmod 755 /etc/skel/autostart/*.sh || true
chmod +x /etc/skel/autostart/*.sh || true

chmod 644 /etc/systemd/system/*.service || true
chown root:root /usr/bin/*

chmod 4755 /usr/bin/sudo
chmod 0644 /etc/sudo.conf
chmod 0644 /etc/sudoers

# IMPORTANT: Set permissions so that everyone can read them
chmod 644 /etc/xdg/autostart/kader42-watcher.desktop || true

chmod 777 /home/liveuser/Desktop/calamares.desktop

echo -e "\x1b[43m\e[38;5;20m 🧹 clean up calamares directories \e[0m"
rm -rf $shareCalamares

echo -e "\x1b[38;5;208m |==========================================| \e[0m"
echo -e "\x1b[38;5;208m |✍🏼| create needed calamares directories...|\e[0m"
echo -e "\x1b[38;5;208m |==========================================| \e[0m"
echo

mkdir -p "$shareCalamares"
mkdir -p "$modules"
mkdir -p "$branding"
mkdir -p "$qmlCalamares"
mkdir -p "$calamaresScripts"
mkdir -p "$usrLibCalamares"
mkdir -p "$usrModules"
mkdir -p "$bootloaderLib"
mkdir -p "$tmpEtc"
mkdir -p "$oneShotPreparerLib"

echo -e "\x1b[95m\e[1;96m |=========================================================================| \e[0m"
echo -e "\x1b[95m\e[1;96m | 🗐 | Copy the calamares configuration files to the needed directories... | \e[0m"
echo -e "\x1b[95m\e[1;96m |=========================================================================| \e[0m"

cp -r $tmpCalamares/modules/. $modules
cp -r $tmpCalamares/branding/. $branding
cp -r $tmpCalamares/qml/. $qmlCalamares
cp -r $tmpCalamares/scripts/. $calamaresScripts
cp -r $tmpCalamares/settings.conf /usr/share/calamares
cp -R $tmpCalamares/linux-preset /usr/share/calamares
cp -r $tmpBootloaderLib/* $bootloaderLib
cp -r $tmpBootloaderLib/* $bootloaderLib
cp -r $tmpOneShotPreparer/* $oneShotPreparerLib
cp -R $tmpEtc/* /etc

chmod +x $calamaresScripts/*.sh

echo -e "\x1b[43m\e[38;5;20m |==================================================================================| \e[0m"
echo -e "\x1b[43m\e[38;5;20m | ⚙️ | Configure a delay for the SDDM startup so that Plymouth does not flicker... | \e[0m"
echo -e "\x1b[43m\e[38;5;20m |==================================================================================| \e[0m"
echo

# Ordner für den Override erstellen
mkdir -p /etc/systemd/system/sddm.service.d/

# Den SDDM-Start so verzögern, dass Plymouth nicht flackert
echo "[Unit]
After=plymouth-quit.service,plymouth-killer.service
Conflicts=plymouth-quit.service, plymouth-killer.service

[Service]
# Plymouth erst beenden, wenn SDDM wirklich den Grafik-Buffer übernimmt
ExecStartPre=-/usr/bin/plymouth deactivate
ExecStopPost=-/usr/bin/plymouth quit" > /etc/systemd/system/sddm.service.d/override.conf

echo
echo -e "\x1b[43m\e[38;5;20m |===================================|\e[0m"
echo -e "\x1b[43m\e[38;5;20m | ⚙️ | Enforce systemd presets now! | \e[0m"
echo -e "\x1b[43m\e[38;5;20m |===================================|\e[0m"
systemctl preset-all
echo

# Add flathub repo system-wide
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Download only the metadata (AppStream) without installing any apps
# This fills /var/lib/flatpak/appstream in the image
flatpak update --appstream

cat <<EOF > /etc/profile.d/flatpak-paths.sh
if [ -d /var/lib/flatpak/exports/share ]; then
    export XDG_DATA_DIRS="/var/lib/flatpak/exports/share:\$XDG_DATA_DIRS"
fi
EOF
chmod +x /etc/profile.d/flatpak-paths.sh

pacman -Sy                  # Synchronisiert die pacman-Datenbanken
appstreamcli refresh-cache --force  # Baut die grafische Datenbank für Pamac/Discover

# mkdir -p /usr/lib/systemd/user/graphical-session.target.wants/
# ln -sf /usr/lib/systemd/user/kader42-watcher.service \
#        /usr/lib/systemd/user/graphical-session.target.wants/kader42-watcher.service

# Pfad im airootfs anlegen
mkdir -p /usr/lib/systemd/user/default.target.wants/

# Symlink händisch setzen
ln -s /usr/lib/systemd/user/kader42-event-listener.service \
      /usr/lib/systemd/user/default.target.wants/kader42-event-listener.service

# Search for 61-framework.hwdb in whole image, but ignore the one in /etc/udev/hwdb.d/ (because we will rotate it there)
find / -name "$hwdFilename" ! -path "$hwdbDir/*" -delete

# 3. IMPORTANT: Build the HWDB ONLY AFTERWARDS
systemd-hwdb update
sync

echo -e "\x1b[32m[Kader42-Final-Check] Verify HWDB status...\e[0m"
# Show all remaining HWDB files on the system
find / -name "*.hwdb" -path "*/udev/hwdb.d/*"

# Reindex HWDB (IMPORTANT for rotation!)
udevadm trigger

echo -e "\x1b[33m[Kader42-Audit] Check for HWDB duplicates...\e[0m"

# Search for all instances of 61-framework.hwdb throughout the entire image
HWDB_COUNT=$(find / -name "$hwdFilename" | wc -l)

if [ "$HWDB_COUNT" -gt 1 ]; then
    echo "!!! CRITICAL ERROR: $HWDB_COUNT Copies of $hwdFilename found!" >&2
    find / -name "$hwdFilename" >&2
    exit 1
elif [ "$HWDB_COUNT" -eq 0 ]; then
    echo "!!! CRITICAL ERROR: Could not find $hwdFilename! Rotation will not work." >&2
    exit 1
else
    echo "[Kader42-Audit] Perfect: Exactly one $hwdFilename file found."
fi

# Display the currently active matrix from the udev perspectivev
echo -ne "\x1b[33mActive matrix: \e[0m"
# udevadm info --export-db | grep "ACCEL_MOUNT_MATRIX" || echo "NO MATRIX FOUND!"
# Simulate the query for the framework sensor (use the Modalias from the file)
systemd-hwdb query "sensor:modalias:platform:cros-ec-accel:*" || echo "NO MATRIX FOUND!"

echo -e "\x1b[43m\e[38;5;20m | ⚙️ |=======================| \e[0m"
echo -e "\x1b[43m\e[38;5;20m | ⚙️ | Set Plymouth-Theme... | \e[0m"
echo -e "\x1b[43m\e[38;5;20m | ⚙️ |=======================| \e[0m"

# plymouth-set-default-theme kader42-mello -R

echo
echo -e "\x1b[44m\e[1;118m  |================================|\e[0m"
echo -e "\x1b[44m\e[1;118m  | customize_airootfs.sh DONE! ✅️ |\e[0m"
echo -e "\x1b[44m\e[1;118m  |================================|\e[0m"