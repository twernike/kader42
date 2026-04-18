#!/bin/bash

while true; do
    # 1. Teste, ob der Proxy überhaupt auf D-Bus reagiert
    if ! gdbus introspect --system --dest net.hadess.SensorProxy --object-path /net/hadess/SensorProxy > /dev/null 2>&1; then
        echo "Proxy reagiert nicht auf D-Bus. Starte Reparatur..."
        
        # 2. Dienst stoppen
        systemctl stop iio-sensor-proxy
        
        # 3. Den Treiber hart entladen und neu laden (Der "Elektroschock")
        # Wir nehmen die gängigen Framework-Module (anpassen falls nötig)
        modprobe -r hid_sensor_accel_3d 2>/dev/null
        modprobe -r hid_sensor_hub 2>/dev/null
        sleep 1
        modprobe hid_sensor_hub
        modprobe hid_sensor_accel_3d
        
        # 4. Dienst wieder starten
        sleep 1
        systemctl start iio-sensor-proxy
        echo "Proxy wurde zwangsweise wiederbelebt."
    fi
    
    # Alle 30 Sekunden prüfen (schont den Akku)
    sleep 30
done