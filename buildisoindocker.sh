#!/bin/bash
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# WICHTIG: Erstelle die Unterordner auf dem Host, damit sie im Mount existieren
mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/packages" "$SCRIPT_DIR/docker-work/work"

CONTAINER_NAME="kaderbuilder"

if ! sudo docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    if sudo docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        sudo docker rm -f $CONTAINER_NAME # Sicherstellen, dass wir keine Rechte-Leichen haben
    fi
    
    echo "Creating new container..."
    # Wir mounten docker-work direkt als Basis
    sudo docker run --privileged --name $CONTAINER_NAME \
            -v "$SCRIPT_DIR":/mydata \
            -v "$SCRIPT_DIR/packages":/packages \
            -v "$SCRIPT_DIR/docker-work":/build-temp \
            archlinux:latest 
fi

sudo docker start $CONTAINER_NAME
# Fix für das Sudo-Problem im Container (Sicherheitsnetz)
sudo docker exec -u root $CONTAINER_NAME chown root:root /usr/bin/sudo
sudo docker exec -u root $CONTAINER_NAME chmod 4755 /usr/bin/sudo

echo "Executing buildiso.sh..."
# Wir wechseln vorher ins Verzeichnis /mydata
sudo docker exec -it $CONTAINER_NAME /bin/bash -c "cd /mydata && ./buildiso.sh build-custom"