#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime
import sys

SETTINGS_FILE = "/etc/kader42/software-center.json"

if not os.path.exists(SETTINGS_FILE):
    sys.exit(0)

try:
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
except:
    sys.exit(0)

# Wenn automatische Updates in der JSON deaktiviert sind, abbrechen
if not data.get("auto_updates", False):
    sys.exit(0)

# Aktuelle Uhrzeit (HH:MM) mit der Wunschzeit vergleichen
now = datetime.now().strftime("%H:%M")
update_time = data.get("update_time", "04:00")

if now == update_time:
    print(f"[{datetime.now()}] Starte geplante automatische Updates...")
    # Läuft nativ als Root, kein pkexec notwendig!
    subprocess.run("/usr/bin/yay -Syu --noconfirm", shell=True)