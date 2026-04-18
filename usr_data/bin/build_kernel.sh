#!/bin/bash

# --- KONFIGURATION ---
KERNEL_DIR="$(pwd)"
BUILD_DEST="$HOME/framework_kernel_build"
THREADS=$(nproc)

echo "--- Starte Framework Kernel Build Prozess ---"
echo "Arbeitsverzeichnis: $KERNEL_DIR"
echo "Zielverzeichnis für ISO-Dateien: $BUILD_DEST"

# 1. Verzeichnisse vorbereiten
mkdir -p "$BUILD_DEST"

# 2. Konfiguration prüfen
if [ ! -f .config ]; then
    echo "Fehler: Keine .config gefunden! Bitte 'make nconfig' zuerst ausführen."
    exit 1
fi

# 3. Kompilieren (Der Hauptgang)
echo "Kompiliere Kernel und Module mit $THREADS Kernen..."
make -j$THREADS || { echo "Build fehlgeschlagen!"; exit 1; }

# 4. Module isoliert installieren (Nicht ins System!)
echo "Installiere Module nach $BUILD_DEST..."
make INSTALL_MOD_PATH="$BUILD_DEST" modules_install

# 5. Kernel-Image kopieren
echo "Kopiere Kernel-Image (bzImage)..."
cp arch/x86/boot/bzImage "$BUILD_DEST/vmlinuz-linux70-framework"

# 6. Aufräumen der Symlinks (Wichtig für die ISO)
# Die Standard-Installation erstellt Links auf den Build-Ordner, 
# die auf der ISO ins Leere laufen würden.
find "$BUILD_DEST/lib/modules" -type l -exec rm {} +

echo "--- FERTIG! ---"
echo "Deine Dateien für die ISO liegen in: $BUILD_DEST"
echo "Dort findest du das Image 'vmlinuz-linux70-framework' und den 'lib' Ordner."