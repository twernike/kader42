#!/usr/bin/env bash
set -e

sudoersd="/etc/sudoers.d"
liveuser="liveuser"
desktopdir="/etc/skel/Desktop"
calamares="$desktopdir/calamares.desktop"

# User im CHROOT anlegen

echo "Create user $liveuser..."
if ! id "$liveuser" &>/dev/null; then
    useradd -m -s /bin/bash -G wheel,audio,video,network "$liveuser"
fi


# Passwort setzen (optional)
echo "$liveuser:$liveuser" | chpasswd

# sudoers
mkdir -p "$sudoersd"
echo "$liveuser ALL=(ALL) NOPASSWD: ALL" > "$sudoersd/$liveuser"
chmod 440 "$sudoersd/$liveuser"

# skel Desktop
mkdir -p "$desktopdir"

cat > "$calamares" << EOF
[Desktop Entry]
Type=Application
Name=Install Kader⁴²
Comment=Install Kader⁴²
Exec=pkexec /usr/bin/calamares
Icon=calamares
Terminal=false
Categories=System;
StartupNotify=true
EOF

chmod +x "$calamares"

# Home Desktop vorbereiten
mkdir -p /home/$liveuser/Desktop
chown -R $liveuser:$liveuser /home/$liveuser/Desktop
