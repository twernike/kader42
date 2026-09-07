sddm="/etc/sddm.conf.d"
kader42_conf="$sddm/kader42.conf"
liveuser="liveuser"

# Verzeichnis anlegen, falls nicht vorhanden
mkdir -p "$sddm"

# Autologin-Konfiguration erstellen, falls nicht vorhanden
if [[ ! -f "$kader42_conf" ]]; then
cat > "$kader42_conf" <<EOF
[Autologin]
User=$liveuser
Session=plasma
EOF
    chmod 644 "$kader42_conf"
fi