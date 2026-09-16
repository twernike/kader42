echo "[create-live-user.sh] Create liveuser..."

# 1. Create groups if they do not exist
# groupadd -g 1000 liveuser 2>/dev/null || true
# getent group wheel >/dev/null || groupadd wheel
# getent group audio >/dev/null || groupadd audio
# getent group video >/dev/null || groupadd video
# getent group input >/dev/null || groupadd input

# 2. Create a user (UID 1000, home directory /home/liveuser, shell /usr/bin/zsh)
if ! id "liveuser" &>/dev/null; then
    /usr/bin/useradd -u 1000 -G adm,wheel,uucp,audio,video,input -c "Live User" -p '' -d /home/liveuser -s /usr/bin/zsh -m liveuser
fi

# 2. Create a user (UID 1000, home directory /home/liveuser, shell /usr/bin/zsh)
# mkdir -p /home/liveuser

if [ -d "/liveuser_home_tmp" ]; then
    cp -a /liveuser_home_tmp/. /home/liveuser/
    rm -rf /liveuser_home_tmp
fi

# 4. Add an XDG folder
su - liveuser -c "xdg-user-dirs-update"

# 5. Finalize the rights
# chown -R 1000:1000 /home/liveuser
# chmod 700 /home/liveuser