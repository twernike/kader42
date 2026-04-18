import time
import subprocess
import os

# CONFIGURATION
SENSOR_PATH = "/sys/bus/iio/devices/iio:device1" # Anpassen (0 oder 1)
THRESHOLD = 5000 # Schwellenwert für die Gravitation
CHECK_INTERVAL = 1.0 # Sekunden

def get_accel(axis):
    try:
        with open(f"{SENSOR_PATH}/in_accel_{axis}_raw", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def set_rotation(kde_rotation_value):
    # D-Bus Befehl für KWin (KDE Wayland)
    # 0: None, 1: 90°, 2: 180°, 3: 270°
    cmd = [
        "dbus-send", "--session", "--type=method_call",
        "--dest=org.kde.KWin", "/org/kde/KWin",
        "org.kde.KWin.setCurrentConfigValue",
        "string:KWinScreenRotation", f"int32:{kde_rotation_value}"
    ]
    subprocess.run(cmd)

last_state = -1

while True:
    if not os.path.exists(SENSOR_PATH):
        print("Sensor not found, please wait...")
        time.sleep(5)
        continue

    x = get_accel("x")
    y = get_accel("y")

    # Sehr simple Logik (muss ggf. an deine Matrix angepasst werden)
    new_state = last_state
    if y > THRESHOLD: new_state = 0   # Normal
    elif y < -THRESHOLD: new_state = 2 # Upside Down
    elif x > THRESHOLD: new_state = 3  # Right
    elif x < -THRESHOLD: new_state = 1 # Left

    if new_state != last_state:
        set_rotation(new_state)
        last_state = new_state

    time.sleep(CHECK_INTERVAL)