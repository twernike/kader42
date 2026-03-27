# 1. Alle bestehenden NM-Verbindungen löschen
echo "Delete all NetworkManager connections"

/usr/bin/nmcli -t -f UUID connection show | while read -r uuid; do
    /usr/bin/nmcli connection delete uuid "$uuid" || true
done

echo "Create new DHCP Ethernet connection"

# 2. Ethernet-Devices suchen und DHCP-Verbindung anlegen
/usr/bin/nmcli -t -f DEVICE,TYPE,STATE device | \
while IFS=: read -r dev type state; do
    if [ "$type" = "ethernet" ]; then
                nmcli connection add \
                type ethernet \
                ifname "$dev" \
                con-name "auto-$dev" \
                ipv4.method auto \
                ipv6.method auto \
                connection.permissions "" \
                connection.autoconnect yes \
                connection.autoconnect-priority 100 \
                connection.zone "" \
                connection.lldp disable  
        
        /usr/bin/nmcli device connect "$dev" || true
    fi
done