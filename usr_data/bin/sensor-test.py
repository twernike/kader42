import os
import selectors
import subprocess
import sys

def find_accelerometer():
    """Sucht nach dem ersten Gerät, das Beschleunigungsdaten liefert."""
    base_path = "/sys/bus/iio/devices/"
    if not os.path.exists(base_path):
        return None, None

    for dev in sorted(os.listdir(base_path)):
        # Ein Accelerometer erkennt man an den 'in_accel_..._en' Dateien
        check_path = os.path.join(base_path, dev, "scan_elements/in_accel_x_en")
        if os.path.exists(check_path):
            with open(os.path.join(base_path, dev, "name"), "r") as f:
                name = f.read().strip()
            return os.path.join(base_path, dev), name
    return None, None

def set_rotation(kde_rotation):
    """Nutzt kscreen-doctor, um die Rotation in Plasma/Wayland zu setzen."""
    # Hinweis: In einer finalen Version könnte man hier noch den Output-Namen 
    # (z.B. eDP-1) dynamisch ermitteln.
    try:
        subprocess.run(["kscreen-doctor", f"output.eDP-1.rotation.{kde_rotation}"], check=True)
    except Exception as e:
        print(f"Fehler beim Rotieren: {e}")

def run_universal_daemon():
    print("--- 🛠️ MyDistro Sensor-Daemon (KDE/Wayland) ---")
    
    dev_path, dev_name = find_accelerometer()
    if not dev_path:
        print("❌ Fehler: Keine kompatible Hardware gefunden.")
        sys.exit(1)
    
    dev_id = os.path.basename(dev_path)
    print(f"✅ Hardware erkannt: {dev_name} ({dev_id})")

    # Buffer scharf schalten
    try:
        with open(f"{dev_path}/scan_elements/in_accel_x_en", "w") as f: f.write("1")
        with open(f"{dev_path}/scan_elements/in_accel_y_en", "w") as f: f.write("1")
        with open(f"{dev_path}/buffer/enable", "w") as f: f.write("1")
    except OSError as e:
        print(f"❌ Kernel-Fehler: Buffer konnte nicht aktiviert werden ({e})")
        sys.exit(1)

    print("🚀 Überwachung aktiv. Nutze KDE KScreen-Interface...")

    # Hier würde jetzt die Logik folgen, die Rohdaten in 
    # 'none', 'left', 'right' oder 'inverted' übersetzt.
    # Für den Test bleiben wir beim 'Hello World' Output.
    
    dev_node = f"/dev/{dev_id}"
    with open(dev_node, "rb") as f:
        selector = selectors.DefaultSelector()
        selector.register(f, selectors.EVENT_READ)
        while True:
            if selector.select(timeout=1.0):
                data = f.read(16)
                print(f"✨ Event auf {dev_name}: Hardware-Daten empfangen!")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("Root-Rechte erforderlich!")
        sys.exit(1)
    run_universal_daemon()