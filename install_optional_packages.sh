#!/bin/bash

# Das Argument ist z.B. "chrome,vscode" oder "chrome"
SELECTION_STRING="$1"

TARGET_USER=$(grep "1000:1000" /etc/passwd | cut -d: -f1)
# Fallback, falls Variable gesetzt ist
if [ -z "$TARGET_USER" ]; then
    TARGET_USER="$CALAMARES_TARGET_USERNAME"
fi

echo "Ausgewählte Pakete: $SELECTION_STRING"
echo "Ziel-User: $TARGET_USER"

# Funktion zum Installieren
install_aur() {
    PKG=$1
    # Wir nutzen su, um als User im Chroot zu agieren.
    # WICHTIG: Das Netzwerk muss im Chroot verfügbar sein.
    su - $TARGET_USER -c "yay -S --noconfirm $PKG"
}

# Prüfen ob 'chrome' im String enthalten ist
if [[ "$SELECTION_STRING" == *"chrome"* ]]; then
    echo "Installiere Chrome..."
    install_aur "google-chrome"
fi

# Prüfen ob 'vscode' im String enthalten ist
if [[ "$SELECTION_STRING" == *"vscode"* ]]; then
    echo "Installiere VS Code..."
    install_aur "visual-studio-code-bin"
fi

# Prüfen ob 'vscode' im String enthalten ist
if [[ "$SELECTION_STRING" == *"libreoffice"* ]]; then
    echo "Installiere VS Code..."
    install_aur "libreoffice-fresh"
fi