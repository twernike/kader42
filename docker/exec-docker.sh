# ToDo: Add a check if the container exists and is running, if not start it or create it if it does not exist
if ! sudo docker ps -q -f name=kaderbuilder | grep -q .; then
    if sudo docker ps -aq -f name=kaderbuilder | grep -q .; then
        sudo docker start kaderbuilder
    else
        sudo docker run --privileged --name kaderbuilder -it -v ~/MyDistriData:/mydata -v ~/MyDistriData/packages:/packages \
                -v ~/docker-work:/build-temp \
                --workdir /build \
                archlinux:latest \
                /bin/bash
        fi
fi
sudo docker exec -it kaderbuilder /bin/bash