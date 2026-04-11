#!/bin/bash

mydataDir="/mydata"
dockerData=$mydataDir/data
isoDir=$dockerData/out
build_temp="/build-temp"
workDir=$build_temp/work

# Wechselt automatisch in das Verzeichnis, in dem das Skript liegt
cd $mydataDir

# Debug-Ausgabe, damit du siehst, wo du arbeitest
echo -e "\e[1;34m 📂 Working directory set to: $(pwd)\e[0m"

function showHelp()
{

echo -e "\e[1;92m ██████████████████████████████████████████████████████████████████████████████████████████████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████
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
 ██████████████████████████████████████████████████████████████████████████████████████████████████
 ████████████     ██████     ████             ████     ███████████             ██████     █████████
 ████████████     ██████     ████             ████     ███████████               ████     █████████
 ████████████     ██████     ████     ████████████     ███████████     ████      ████     █████████
 ████████████                ████             ████     ███████████     ███       ████     █████████
 ████████████                ████             ████     ███████████              █████    ██████████
 ████████████     ██████     ████     ████████████     ███████████     ████████████████████████████
 ████████████     ██████     ████             ████             ███     ██████████████     █████████
 ████████████     ██████     ████             ████             ███     ██████████████     █████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████
 ██████████████████████████████████████████████████████████████████████████████████████████████████\e[0m"


    echo -e "\e[1;92m 
 It is not necessary to pass any parameters. 
 However, you can optionally set the following parameters if desired:\e[0m"
    echo 
    echo -e "\e[1;92m build-custom   ➤
 ============  
    Builds the packages from the AUR that were specified in build_packages.sh 
    and makes them available in a custom repository for the live system. 
    This makes it possible to simply list the packages in packages.x86_64, 
    allowing mkarchiso to install them into airootfs via pacman.
    The custom repository is intended only for the live system 
    and is not included in an installation. 
    However, the installed packages are, of course, copied over. \e[0m"
    echo
    echo -e "\e[1;92m create-build-user ➤
    Creates a user named 'builduser' with passwordless sudo rights for building 
    the AUR packages. If no user with the name 'builduser' exists, it will be created.
    You have to this parameter, if you set the build-custom parameter and the user doesn't exist, 
    because the AUR packages need to be built as a non-root user."
    echo
    echo -e "\e[1;92m generate-icons ➤
 ============== 
    Converts the icons copied to the icons subdirectory to the correct sizes,
    creates the appropriate directory structure, and copies them to the correct
    location in airootfs.   \e[0m"
    echo
    echo -e "\e[1;92m help           ➤  Show this helptext. \e[0m"
    exit 1
}

# Funktion: Sicherstellen, dass Verzeichnisse wirklich weg sind
# Nutzung: force_remove "/pfad/zum/ordner"
force_remove() {
    local target="$1"
    
    if [ -d "$target" ] || [ -f "$target" ]; then
        echo "[force_remove] Try to delete: $target ..."
        
        # 1. Attempt: Normal deletion
        rm -rf "$target" 2>/dev/null
        
        # 2. Check: Is it still there? (Due to mounts or Docker locks)
        if [ -e "$target" ]; then
            echo "[force_remove] WARNING: $target is persistent. Attempting to unmount..."
            umount -l "$target" 2>/dev/null
            rm -rf "$target"
        fi
        
        # 3. Final check: If it's still there -> Abort!
        if [ -e "$target" ]; then
            echo "!!! ERROR: Could not remove $target. Build will be stopped!" >&2
            exit 1
        fi
        echo "[✅️ force_remove] Success: $target has been removed."
    fi
}


if [[ "$1" == "help" ]]; then
    showHelp
fi

buildUser="admin"

# ==============================
# Configuration
# ==============================
releng="releng"
airootfs="$releng/airootfs"
LOCAL_PACKAGES="/packages"
LOCAL_REPO="$LOCAL_PACKAGES/custom"
REPO_DB="$LOCAL_REPO/custom.db.tar.zst"
etc="$airootfs/etc"
usr_share="$airootfs/usr/share"
usr_lib="$airootfs/usr/lib"
usr_systemd="$usr_lib/systemd"
shareIcons="$usr_share/icons"
# Plasma KDE Share directory (for wallpapers in this case)
sharePlasma="$usr_share/plasma"
plasmaWallpapers="$sharePlasma/wallpapers"
kader42Wallpapers="$plasmaWallpapers/org.kader42.wallpaper"

# Plymouth theme paths
share_plymouth="$usr_share/plymouth"
plymouth_themes="$share_plymouth/themes"
kader42_plymouth="$plymouth_themes/kader42"

sharePolkit="$usr_share/polkit-1"
polkitActions="$sharePolkit/actions"

rootpath="$airootfs/root"
kaderCalamares="calamares-kader-config"
shareCalamares="$airootfs/usr/share/calamares"
etcCalamares="$airootfs/etc/calamares"
liveuserHome="$airootfs/home/liveuser"
os_release="os-release-info/os-release"
etc_conf="etc_conf"
builduser="builduser"
BUILD_DIR="/build"

# temporary folders for the build process (will be deleted afterwards)
etc_tmp="$airootfs/etc_tmp"
os_release_tmp="$airootfs/os-release-tmp"
tmpUsr="$airootfs/usr_tmp"
rootCalamares="$airootfs/$kaderCalamares"
bootdir_tmp="$airootfs/boot_tmp"
packages="$airootfs/packages/"
customRepo="$packages/custom"


# Get the line “ID=” from /etc/os-release
echo -e "\e[1;34m 🕵 Check whether it is an Arch Linux installation...\e[0m"
OS_ID=$(grep "^ID=" /etc/os-release | cut -d= -f2)

if [[ "$OS_ID" != "arch" ]]; then
    echo -e  "\x1b[43m\e[1;31m❌ This script may only be run on Arch Linux and not on $OS_ID!\e[0m"
    exit 1
fi

cat <<'EOF'
      __O                                               
     / /\_,                                             
   ___/\                                                
       /_ ____                    _                     
         |  _ \ _   _ _ __  _ __ (_)_ __   __ _         
         | |_) | | | | '_ \| '_ \| | '_ \ / _` |        
         |  _ <| |_| | | | | | | | | | | | (_| |        
         |_| \_\\__,_|_| |_|_| |_|_|_| |_|\__, |        
                                          |___/         
 ____        _ _     _      ____            _       _   
| __ ) _   _(_) | __| |    / ___|  ___ _ __(_)_ __ | |_ 
|  _ \| | | | | |/ _` |____\___ \ / __| '__| | '_ \| __|
| |_) | |_| | | | (_| |_____|__) | (__| |  | | |_) | |_ 
|____/ \__,_|_|_|\__,_|    |____/ \___|_|  |_| .__/ \__|
                                             |_|        
        __              _  __         _                 
       / _| ___  _ __  | |/ /__ _  __| | ___ _ __42     
      | |_ / _ \| '__| | ' // _` |/ _` |/ _ \ '__|      
      |  _| (_) | |    | . \ (_| | (_| |  __/ |         
      |_|  \___/|_|    |_|\_\__,_|\__,_|\___|_|         
EOF

echo
echo -e "\e[1;92m ✅ Arch Linux detected. Script will continue...⏩\e[0m"

echo -e "\e[1;92m 🧹 Clear package cache \e[0m"
pacman -Scc --noconfirm

echo -e "\e[1;92m 🗘 Refreshing and initializing pacman repositories... \e[0m"
pacman -Syyu --noconfirm

echo
echo -e  "\x1b[45m\e[33;1;20m|🧹|=======================|\e[0m"
echo -e  "\x1b[45m\e[33;1;20m|🧹| Start cleanup first...|\e[0m"
echo -e  "\x1b[45m\e[33;1;20m|🧹|=======================|\e[0m"

rm -rf $work_dir
rm -rf out
rm -rf "$airootfs/etc/systemd"
rm -rf "$airootfs/tmp"
rm -rf "$airootfs/usr_tmp"
rm -rf "$airootfs/etc_tmp"
rm -rf "$usr_share"
rm -rf "$usr_lib"
rm -rf "$liveuserHome"
rm -rf "$rootCalamares"

chmod 755 usr_data/bin/delete-and-reconnect-network.sh
chown root:root usr_data/bin/delete-and-reconnect-network.sh
chown root:root -R *

# Instead of `chown -R root:root *`
# Only change the directories you're actually using to build the ISO:
chown -R root:root releng data 2>/dev/null || true

./create-live-user.sh

echo
echo -e  "\x1b[43m\e[38;5;20m |✍🏼|=============================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |✍🏼| Create needed directories...|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |✍🏼|=============================|\e[0m"

mkdir -p build
mkdir -p "$build_temp"
mkdir -p "$workDir"
mkdir -p "$liveuserHome"
mkdir -p "$rootpath"
mkdir -p "$usr_share"
mkdir -p "$usr_share"
mkdir -p "$shareIcons"
mkdir -p "$sharePlasma"
mkdir -p "$plasmaWallpapers"
mkdir -p "$kader42Wallpapers"
mkdir -p "$share_plymouth"
mkdir -p "$sharePolkit"
mkdir -p "$polkitActions"
mkdir -p "$tmpUsr"
mkdir -p "$LOCAL_PACKAGES"
mkdir -p "$LOCAL_REPO"
mkdir -p "$etc_tmp"
mkdir -p "$os_release_tmp"
mkdir -p "$packages"
mkdir -p "$customRepo"

echo -e  "\x1b[43m\e[38;5;20m |✍🏼|=====================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |✍🏼| Set ownership of airootfs to root...|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |✍🏼|=====================================|\e[0m"

chown -R root:root *
chmod -R 755 $airootfs
chown -R root:root "$airootfs"

echo -e  "\x1b[43m\e[38;5;20m |Refresh pacman database|\e[0m"
pacman -Syyu --noconfirm

echo -e  "\e[1;92m|⚒️|===============================|\e[0m"
echo -e "\e[1;92m |⚒️| Install other needed packages |\e[0m"
echo -e  "\e[1;92m|⚒️|===============================|\e[0m"

pacman -S --needed libinput systemd-libs base-devel sudo git --noconfirm

echo -e "\x1b[43m\e[38;5;20m 🗘 ==================================================\e[0m"
echo -e "\x1b[43m\e[38;5;20m 🗘 Refreshing and initializing pacman repositories...\e[0m"
echo -e "\x1b[43m\e[38;5;20m 🗘 ==================================================\e[0m"

echo
echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| Check whether archiso is already installed |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| or still needs to be installed...          |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"

pacman -Q archiso > /dev/null 2>&1

#$? contains the exit code of the last command
if [ $? -eq 0 ]; then
    echo -e "\e[1;92m ⏩ Package archiso already installed. Continue script...\e[0m"
else
    echo -e "\e[1;95m 👨‍🔧 Package archiso is not installed. Install archiso first...\e[0m"
    pacman -S archiso sudo --noconfirm
fi

echo -e  "\x1b[43m\e[38;5;20m |🕵|========================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| Check if the linux kernel is installed |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵|========================================|\e[0m"
pacman -Q linux > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "\e[1;92m ⏩ Package linux already installed. Continue script...\e[0m"
else
    echo -e "\e[1;95m 👨‍🔧 Package linux is not installed. Install linux first...\e[0m"
    pacman -S linux  --noconfirm
fi

echo -e "\e[1;92m | ✍🏼| Copy linux.preset to airootfs |\e[0m"
mkdir -p "$kaderCalamares/linux-preset"
cp /etc/mkinitcpio.d/linux.preset "$kaderCalamares/linux-preset"
cp -r "$etc_conf/." "$etc_tmp"

echo -e  "\x1b[43m\e[38;5;20m |🕵|==================================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| Check if the linux firmware package is installed |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵|==================================================|\e[0m"
pacman -Q linux-firmware > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "\e[1;92m ⏩ Package linux already installed. Continue script...\e[0m"
else
    echo -e "\e[1;95m 👨‍🔧 Package linux is not installed. Install linux first...\e[0m"
    pacman -S linux-firmware  --noconfirm
fi


# echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"
# echo -e  "\x1b[43m\e[38;5;20m |🕵| Check if the plymouth package is installed |\e[0m"
# echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"
# pacman -Q plymouth > /dev/null 2>&1

# if [ $? -eq 0 ]; then
#     echo -e "\e[1;92m ⏩ Package plymouth already installed. Continue script...\e[0m"
# else
#     echo -e "\e[1;95m 👨‍🔧 Package plymouth is not installed. Install plymouth first...\e[0m"
#     pacman -S plymouth  --noconfirm
# fi


echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| Check if the mkinitcpio-archiso package is installed |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵|============================================|\e[0m"
pacman -Q mkinitcpio-archiso > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "\e[1;92m ⏩ Package mkinitcpio-archiso already installed. Continue script...\e[0m"
else
    echo -e "\e[1;95m 👨‍🔧 Package mkinitcpio-archiso is not installed. Install it first...\e[0m"
    pacman -S mkinitcpio-archiso  --noconfirm
fi


if [[ $1 == create-build-user || $2 == create-build-user || $3 == create-build-user ]]; then

    echo -e "\e[1;92m |⚒️| Create user $builduser for building the AUR packages |\e[0m"
    ./create_builduser.sh
fi

echo -e "🔨  \x1b[43m\e[38;5;20m Install needed packages for building custom packages...\e[0m"
pacman -S --needed git base-devel libhandy libadwaita flatpak --noconfirm

echo -e "\e[1;92m | ⬇️ ⚒️| Create directory $airootfs/etc|\e[0m"
mkdir -p "$airootfs/etc"
echo -e "\e[1;92m | ⬇️ ⚒️| Create directory $airootfs/etc/mkinitcpio.d|\e[0m"
mkdir -p "$airootfs/etc/mkinitcpio.d"
echo -e "\e[1;92m | ⬇️ ⚒️| Create directory $airootfs/home|\e[0m"

mkdir -p "$airootfs/home"
echo -e "\e[1;92m | ⬇️ ⚒️| Create directory $airootfs/home/liveuser|\e[0m"
mkdir -p "$airootfs/home/liveuser"
echo -e "\e[1;92m | ⬇️ ⚒️| Create directory $airootfs/home/liveuser/Desktop|\e[0m"
mkdir -p "$airootfs/home/liveuser/Desktop"
mkdir -p "$airootfs/home/liveuser/.config"
mkdir -p "$airootfs/home/liveuser/.config/autostart"


if [[ $1 == build-custom || $2 == build-custom || $3 == build-custom ]]; then
    echo -e "\e[1;92m | ⬇️ ⚒️|-------------------------------------------------------------|\e[0m"
    echo -e "\e[1;92m | ⬇️ ⚒️| Download AUR packages and build packages for custom repo... |\e[0m"
    echo -e "\e[1;92m | ⬇️ ⚒️|-------------------------------------------------------------|\e[0m"

    chown -R $builduser "$LOCAL_PACKAGES"
    chmod -R 777 build
    chmod -R 777 /packages

    mkdir -p $BUILD_DIR
    chown -R $builduser:$builduser $BUILD_DIR
    # su $builduser ./build_packages.sh > build_packages.log
    su $builduser -c "./build_packages.sh 2>&1 | tee build_packages_$(date +%Y%m%d_%H%M%S).log"
    cp -R /packages "$airootfs"
    pacman -Syyu --noconfirm
fi

echo -e "\e[1;92m Copy pacman.conf to container... \e[0m"
cp $releng/pacman.conf /etc/pacman.conf
cp $os_release $os_release_tmp

if [[ ! -f "$REPO_DB" ]]; then
    echo "custom repo DB missing - create it now..."
    repo-add "$REPO_DB" "$LOCAL_REPO"/*.pkg.tar.*
    pacman -Syyu --noconfirm
fi

if [[ $1 == generate-icons || $2 == generate-icons || $3 == generate-icons ]]; then
    echo 
    echo -e "\x1b[43m\e[1;34m |⚒️|-------------------|\e[0m"
    echo -e "\x1b[43m\e[1;34m |⚒️| Generate Icons... |\e[0m"
    echo -e "\x1b[43m\e[1;34m |⚒️|-------------------|\e[0m"

    icons/generate-icons.sh
fi

echo "copy local packages to the airootfs..."
cp -R $LOCAL_PACKAGES "$airootfs" # Directories will be created automatically
chown -R root:root "$LOCAL_PACKAGES"
chown -R root:root "$airootfs/packages/custom"
# sudo chown -R root:root "$airootfs/packages/base"

echo -e "\x1b[43m\e[38;5;20m 🗘 Refreshing pacman repositories after building custom packages...\e[0m"
pacman -Syyu --noconfirm

echo -e "\x1b[43m\e[38;5;20m ✏️ Adjusting the permissions on /etc/skel\e[0m"
cp -r etc_conf/* $airootfs/etc

echo -e "\x1b[43m\e[38;5;20m 🗐 Copy etc-Configuration-Data\e[0m"
chmod -R 755 $airootfs/etc/skel/

echo -e "\x1b[43m\e[38;5;20m 🗐 Copy usr-data to /usr_temp\e[0m"
cp -R usr_data/* "$tmpUsr"

echo -e "\x1b[43m\e[38;5;20m 🗐 Copy calamares desktop file to liveuser home directory\e[0m"
cp -R liveuser_home/* "$airootfs/home/liveuser/"
cp -R liveuser_home/.config "$airootfs/home/liveuser/"

echo -e "\e[1;35m 🗐 Copy some scripts to CHROOT\e[0m"
cp customize_airootfs.sh $rootpath

echo -e "\x1b[43m\e[38;5;20m 🗐 Copy calamares config to CHROOT"

mkdir -p $rootCalamares
cp -r $kaderCalamares/* $rootCalamares

echo -e "\x1b[43m\e[38;5;20m 🗘 Refreshing pacman repositories...\e[0m"
pacman -Syyu --noconfirm

echo 
echo -e "\x1b[43m\e[1;34m |⚒️|--------------------------------------|\e[0m"
echo -e "\x1b[43m\e[1;34m |⚒️| Build ISO file with mkarchiso  💿... |\e[0m"
echo -e "\x1b[43m\e[1;34m |⚒️|--------------------------------------|\e[0m"

# mkarchiso -r -v -w /build/archiso-work -o /mydata/archlive/out releng -C
mkarchiso -r -v -w $workDir -o $isoDir releng -C
chown -R $USER:$USER .

echo
echo -e "\x1b[92m\e[1;118m |=================================================| \e[0m"
echo -e "\x1b[92m\e[1;118m | 👉🗑️ | Remove temporary directories and files..  | \e[0m"
echo -e "\x1b[92m\e[1;118m |=================================================| \e[0m"

# 1. Make sure nothing is mounted anymore
sync

etc_tmp="$airootfs/etc_tmp"
build_temp="/build-temp"
os_release_tmp="$airootfs/os-release-tmp"
tmpUsr="$airootfs/usr_tmp"
rootCalamares="$airootfs/$kaderCalamares"
bootdir_tmp="$airootfs/boot_tmp"

# 2. Aggressive deletion with verification
TEMP_DIRS=("$etc_tmp" "$build_temp" "$os_release_tmp" "$bootdir_tmp"  "$tmpUsr" "$rootCalamares")

for dir in "${TEMP_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "[Kader42-Builder] Try to delete folder: $dir"
        force_remove "$dir"
        echo "[Kader42-Builder] Folder $dir deleted"
    fi
done

echo
echo -e "\e[1;92m |============|\e[0m"
echo -e "\e[1;92m | ✅️ | DONE! |\e[0m"
echo -e "\e[1;92m |============|\e[0m"
echo