# ToDo: Add a check if the container exists and is running, if not start it or create it if it does not exist
# Gehe ins Skript-Verzeichnis, dann eins hoch, und nimm davon den absoluten Pfad
PARENT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CONTAINER_NAME="kaderbuilder"
mkdir -p "$PARENT_DIR/data" "$PARENT_DIR/packages" "$PARENT_DIR/docker-work/work"

if ! sudo docker ps -q -f name=kaderbuilder | grep -q .; then
    if sudo docker ps -aq -f name=kaderbuilder | grep -q .; then
        sudo docker start kaderbuilder
    else
    sudo docker run --privileged --name $CONTAINER_NAME -it \
            -v "$PARENT_DIR":/mydata \
            -v "$PARENT_DIR/packages":/packages \
            -v "$PARENT_DIR/docker-work":/build-temp \
            archlinux:latest
        fi
fi
sudo docker exec -it kaderbuilder /bin/bash