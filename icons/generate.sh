#!/bin/bash

if [ $# -ne 3 ]; then
    echo "Error: No parameter was specified for the context and/or theme name.
          Please specify the icon context and the theme name as parameters.
          Possible values for the icon context are:"
    echo "
          -> places
          -> actions
          -> devices
          -> mimetypes
          -> status
          -> categories
          -> apps
          -> emblems
          -> panel
          -> legacy
          -> preferences"
    echo
    echo "Example usage: ./generate_icons.sh <source_dir> <your-theme-name> <icon-context>"
    exit 1
fi

echo
echo -e  "\x1b[43m\e[38;5;20m |🕵|================================================|\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| Check whether imagemagick is already installed |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵| or still needs to be installed...              |\e[0m"
echo -e  "\x1b[43m\e[38;5;20m |🕵|================================================|\e[0m"
echo

pacman -Q imagemagick > /dev/null 2>&1

#$? contains the exit code of the last command
if [ $? -eq 0 ]; then
    echo -e "\e[1;92m ⏩ Package imagemagick already installed. Continue script...\e[0m"
else
    echo -e "\e[1;95m 👨‍🔧 Package imagemagick is not installed. Install imagemagick first...\e[0m"
    pacman -S imagemagick --noconfirm
fi

mkdir -p usr_data/share/icons/

# List of required sizes
SIZES=(16 22 24 32 48 64 128 256)

echo "Start convert for theme: $2..."

# Search for all PNGs in the current directory
for FILE in "$1"/*.png
do
    # Verhindere Fehler, falls keine PNGs gefunden werden
    [ -e "$FILE" ] || continue
    
    # Dateiname ohne Endung extrahieren (z.B. 'start-here-kde')
    FILENAME=$(basename "$FILE" .png)
    
    echo "Process: $FILE"

    for SIZE in "${SIZES[@]}"
    do
        # Zielordner erstellen
        mkdir -p "$2"
        mkdir -p "$2/${SIZE}x${SIZE}"
        DEST_DIR="$2/${SIZE}x${SIZE}/$3"
        mkdir -p "$DEST_DIR"
        
        # Knallharte Skalierung (Pixel-Art freundlich)
        # -sample sorgt für Schärfe
        # -extent sorgt für das 1:1 Quadrat (Padding)
        magick "$FILE" -sample ${SIZE}x${SIZE} \
               -background none -gravity center -extent ${SIZE}x${SIZE} \
               "$DEST_DIR/$FILENAME.png"
    done
done

echo "Create symlinks for Recycle Bin in the theme folder..."

for SIZE in "${SIZES[@]}"
do
    # Pfad innerhalb des frisch erstellten Theme-Ordners
    REL_DIR="$2/${SIZE}x${SIZE}/$3"
    
    if [ -d "$REL_DIR" ]; then
        # Wichtig: Wir gehen in den Ordner, damit der Link 'kurz' bleibt
        pushd "$REL_DIR" > /dev/null
            if [ -f "user-trash-empty.png" ]; then
                ln -sf "user-trash-empty.png" "trash-empty.png"
                ln -sf "user-trash-empty.png" "user-trash.png"
            fi
            if [ -f "user-trash-full.png" ]; then
                ln -sf "user-trash-full.png" "trash-full.png"
            fi
        popd > /dev/null
    fi
done

# mkdir -p usr_data/share/icons/$2
echo "------------------------------------------"
echo "DONE! Symlinks created."
echo "Copy ./$2 to the usr_data/share/icons/ folder..."
sudo cp -a -R icons/$2 usr_data/share/icons/

# Note: ‘cp -a’ is important so that symlinks are copied as links and not as file copies!
