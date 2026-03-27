#!/bin/bash
builduser="builduser"
buildpath="build"

# Versuche die ID des Benutzers abzurufen
id "$builduser" &>/dev/null

# Prüfe den Exit-Status: $? ist 0 bei Erfolg, != 0 bei Fehler (Benutzer nicht gefunden)
if [ $? -ne 0 ]; then
    echo -e "\e[1;92m |⚒️| User'$builduser' does not exist. Creating user... |\e[0m"
    # 1. User anlegen (ohne Passwort-Zwang)
    useradd -m builduser
    echo -e "\e[1;92m |✅| User '$builduser' created. |\e[0m"
else
    echo -e "\e[1;92m |✅| User '$builduser' still exists. |\e[0m"
fi

if [ ! -s "/etc/sudoers.d/$builduser" ]; then
    # 2. Die entscheidende Zeile für sudoers (ohne Syntax-Fehler)
    # Wir nutzen ein separates File in sudoers.d, das ist sauberer
    echo "builduser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$builduser
else
  echo "sudoers file for '$builduser' already exists."
fi

# 3. Berechtigungen sicherstellen (Sudoers Dateien müssen 0440 sein)
chmod 440 /etc/sudoers.d/$builduser
chown -R $builduser $buildpath