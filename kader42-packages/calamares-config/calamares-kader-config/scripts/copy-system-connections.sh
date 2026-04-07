    echo "[NM] Copy NetworkManager connections from live system"

    SRC="/etc/NetworkManager/system-connections"
    DST="/run/archiso/airootfs/etc/NetworkManager/system-connections"

    if [ ! -d "$SRC" ]; then
        echo "[NM] No connections to copy"
        exit 0
    fi

    mkdir -p "$DST"
    cp -a "$SRC/"* "$DST/" || true

    echo "[NM] Fix permissions"
    chown root:root "$DST"/*.nmconnection 2>/dev/null || true
    chmod 600 "$DST"/*.nmconnection 2>/dev/null || true