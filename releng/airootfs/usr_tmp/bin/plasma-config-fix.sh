#!/bin/bash
# Warten, bis der Plasma-Session-Bus erreichbar ist
until qdbus6 org.kde.KWin /KWin org.kde.KWin.supportInformation >/dev/null 2>&1; do
    sleep 1
done

# Meta-Taste in der kwinrc erzwingen
kwriteconfig6 --file kwinrc --group ModifierOnlyShortcuts --key Meta "org.kde.plasmashell,/PlasmaShell,org.kde.PlasmaShell,activateAppletByName,org.kde.plasma.kickoff"

# Die globale Shortcut-Datei bereinigen (Meta-Zuweisung für Kickoff löschen)
kwriteconfig6 --file kglobalshortcutsrc --group plasmashell --key "activate application launcher" "Alt+F1,none,Activate Application Launcher"
kwriteconfig6 --file ~/.config/kglobalshortcutsrc --group plasmashell --key "activate application launcher" "Alt+F1,none,Activate Application Launcher"


# 3. KWin und Shell zum Neuladen zwingen
qdbus6 org.kde.KWin /KWin reconfigure
systemctl --user restart plasma-plasmashell.service