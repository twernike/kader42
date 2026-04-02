#!/bin/bash

TODO_FILE="/var/lib/preinstall/todo.txt"

# 1. Warten auf Internet (wichtig für yay/pacman)
until ping -c 1 google.com &>/dev/null; do sleep 5; done

if [ -f "$TODO_FILE" ]; then
    # Ersten User finden (der in Calamares erstellt wurde)
    USER_NAME=$(id -nu 1000)
    
    # Liste einlesen und installieren
    PKGS=$(cat "$TODO_FILE")
    sudo -u "$USER_NAME" yay -S --noconfirm --needed $PKGS
    
    # --- AUFRÄUMEN ---
    # Liste löschen
    rm "$TODO_FILE"
    # Ordner löschen
    rmdir "/var/lib/preinstall"
    # Service deaktivieren (keine Dateileiche im System-Start)
    systemctl disable firstboot-installer.service
    # Optional: Das Skript selbst löschen
    # rm "$0" 
fi