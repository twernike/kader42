#!/bin/bash
echo
echo -e "\x1b[43m\e[38;5;20m ---------------------------------------\e[0m"
echo -e "\x1b[43m\e[38;5;20m | Start script archiso-livecd-user.sh |\e[0m"
echo -e "\x1b[43m\e[38;5;20m ---------------------------------------\e[0m"

echo
echo -e  "\x1b[43m\e[38;5;20m -----------------------------\e[0m"
echo -e  "\x1b[43m\e[38;5;20m | ✍🏼 # Create user liveuser |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m -----------------------------\e[0m"
echo
# Benutzer erstellen
useradd -m -G wheel,audio,video,storage,lp,power,scanner,optical -s /bin/bash liveuser

echo -e  "\x1b[43m\e[38;5;20m ------------------------------------\e[0m"
echo -e  "\x1b[43m\e[38;5;20m | 🔑 | Create a passwordless login |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m ------------------------------------\e[0m"
# Passwortloses Login
passwd -d liveuser

# Sudo erlauben

echo
echo -e  "\x1b[43m\e[38;5;20m -------------------\e[0m"
echo -e  "\x1b[43m\e[38;5;20m | 🔑 | Allow sudo |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m -------------------\e[0m"

echo "liveuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser
chmod 0440 /etc/sudoers.d/liveuser

echo
echo -e  "\x1b[43m\e[38;5;20m ----------------------------------\e[0m"
echo -e  "\x1b[43m\e[38;5;20m | 🔑 | Set a clean XDG directory |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m ----------------------------------\e[0m"
# XDG-Verzeichnis sauber setzen
mkdir -p /home/liveuser
chown -R liveuser:liveuser /home/liveuser
echo
echo -e "\e[1;92m -------------------------------------"
echo -e "\e[1;92m | ✅️ | archiso-livecd-user.sh DONE! |\e[0m"
echo -e "\e[1;92m -------------------------------------"