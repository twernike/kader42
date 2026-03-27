# Erstelle den Ordner, falls er fehlt
releng="releng"
airootfs="$releng/airootfs"
liveuser_conf="$airootfs/etc/sysusers.d/liveuser.conf"

mkdir -p "$airootfs/etc/sysusers.d/"

if [ ! -f "$liveuser_conf" ]; then
cat <<EOF > "$airootfs/etc/sysusers.d/liveuser.conf"
g liveuser 1000 -
u liveuser 1000 "Live User" /home/liveuser /usr/bin/zsh
m liveuser wheel
m liveuser audio
m liveuser video
m liveuser input
EOF
fi