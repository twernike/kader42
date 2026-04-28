import os
import math
import time
import subprocess

def find_sensors():
    """
    Sucht dynamisch nach Base- und Lid-Accelerometer.
    Gibt ein Dict mit den Pfaden zurück oder None.
    """
    sensors = {'base': None, 'lid': None}
    base_path = "/sys/bus/iio/devices/"
    
    if not os.path.exists(base_path):
        return None

    for dev in os.listdir(base_path):
        full_path = os.path.join(base_path, dev)
        label_file = os.path.join(full_path, "label")
        
        # Methode 1: Über das Label (Best Practice)
        if os.path.exists(label_file):
            with open(label_file, "r") as f:
                label = f.read().strip().lower()
                if "base" in label:
                    sensors['base'] = full_path
                elif "lid" in label or "display" in label:
                    sensors['lid'] = full_path
        
        # Methode 2: Fallback über physikalische Position (falls Label fehlt)
        # Viele Sensoren haben ein 'location' Attribut
        loc_file = os.path.join(full_path, "location")
        if not sensors['base'] or not sensors['lid']:
            if os.path.exists(loc_file):
                with open(loc_file, "r") as f:
                    loc = f.read().strip().lower()
                    if "base" in loc: sensors['base'] = full_path
                    elif "lid" in loc: sensors['lid'] = full_path

    return sensors if (sensors['base'] and sensors['lid']) else None

def read_accel(path):
    """ Liest X, Y, Z Rohdaten eines IIO-Devices """
    try:
        vals = []
        for axis in ['x', 'y', 'z']:
            with open(f"{path}/in_accel_{axis}_raw", "r") as f:
                vals.append(int(f.read().strip()))
        return tuple(vals)
    except:
        return None

def calculate_angle(v1, v2):
    """ Vektorgeometrie: Winkel zwischen zwei 3D-Vektoren """
    dot = sum(a*b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    
    if mag1 == 0 or mag2 == 0: return 0
    
    # Cosinus-Wert begrenzen wegen Float-Präzision
    cos_theta = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_theta))

def main():
    print("Kader⁴² Sensor-Discovery läuft...")
    sensors = find_sensors()
    
    if not sensors:
        print("Kritischer Fehler: Konnte nicht beide Beschleunigungssensoren finden!")
        # Hier könnte man einen Fallback auf den (unzuverlässigen) SW_TABLET_MODE einbauen
        return

    print(f"Sensoren gefunden:\n Base: {sensors['base']}\n Lid:  {sensors['lid']}")

    last_state = -1
    current_state = 0
    
    while True:
        v_base = read_accel(sensors['base'])
        v_lid = read_accel(sensors['lid'])

        if v_base and v_lid:
            angle = calculate_angle(v_base, v_lid)
            
            # Hysterese: 180 Grad ist flach, Tablet ist fast 360 Grad
            # Achtung: Je nach Montage der Sensoren kann 'flach' 0 oder 180 sein.
            # Das muss man einmalig am Framework auslesen.
            if angle > 190:
                new_state = 1
            elif angle < 170:
                new_state = 0
            else:
                new_state = current_state

            if new_state != last_state:
                subprocess.run(["/usr/bin/plasma-convertible-switcher", str(new_state)])
                last_state = new_state
                print(f"Winkel: {angle:.1f}° | Mode: {'TABLET' if new_state == 1 else 'LAPTOP'}")

        time.sleep(2)

if __name__ == "__main__":
    main()