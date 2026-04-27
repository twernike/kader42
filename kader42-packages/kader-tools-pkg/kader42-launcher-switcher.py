#!/usr/bin/env python3
import evdev
from evdev import ecodes
import subprocess
import sys
import os
import time

# --- KONFIGURATION ---
DBUS_SHELL = "org.kde.PlasmaShell"
PATH_SHELL = "/PlasmaShell"
METHOD_JS  = "org.kde.PlasmaShell.evaluateScript"

DBUS_OSD   = "org.kde.plasmashell"
PATH_OSD   = "/org/kde/osdService"
METHOD_OSD = "org.kde.osdService.showText"

class Kader42Listener:
    def __init__(self):
        self.current_mode = None  # 0 = Laptop, 1 = Tablet
        # Sprache einmalig beim Start ermitteln
        self.lang = os.environ.get('LANG', 'de')[:2]

    def get_js_code(self, is_tablet):
        """Erstellt das JS, das nur den Launcher-Typ austauscht."""
        target = "org.kde.plasma.kickerdash" if is_tablet else "org.kde.plasma.kickoff"
        old = "org.kde.plasma.kickoff" if is_tablet else "org.kde.plasma.kickerdash"
        
        return f"""
        var panelsList = panels();
        for (var i = 0; i < panelsList.length; ++i) {{
            var p = panelsList[i];
            var widgets = p.widgets();
            for (var j = 0; j < widgets.length; ++j) {{
                var w = widgets[j];
                if (w.type === "{old}") {{
                    var idx = w.index;
                    w.remove();
                    var newW = p.addWidget("{target}");
                    newW.index = idx;
                    newW.currentConfigGroup = ["Shortcuts"];
                    newW.writeConfig("globalShortcut", "Alt+F1");
                    if ("{target}" === "org.kde.plasma.kickerdash") {{
                        newW.currentConfigGroup = ["General"];
                        newW.writeConfig("showCategories", false);
                    }}
                }}
            }}
        }}
        """

    def show_feedback(self, is_tablet):
        """Sendet OSD für sofortiges Feedback und Notify für die Historie."""
        icon = "tablet" if is_tablet else "computer"
        
        if self.lang == "de":
            label = "Tablet-Modus" if is_tablet else "Notebook-Modus"
            title = "Kader⁴² Hybrid Switch"
            msg = f"{label} aktiviert"
        else:
            label = "Tablet Mode" if is_tablet else "Laptop Mode"
            title = "Kader⁴² Hybrid Switch"
            msg = f"{label} activated"

        # 1. Das native KDE-OSD (zentral, dezent)
        try:
            subprocess.run([
                "qdbus6", DBUS_OSD, PATH_OSD, METHOD_OSD, icon, label
            ], stderr=subprocess.DEVNULL)
        except: pass

        # 2. Die Benachrichtigung (für den Verlauf)
        subprocess.run([
            "notify-send", "-u", "low", "-a", "System", "-i", icon, title, msg
        ])

    def switch_mode(self, value):
        if self.current_mode == value:
            return
        
        self.current_mode = value
        is_tablet = (value == 1)
        
        # JS via qdbus6 absetzen - ASYNCHRON
        js_code = self.get_js_code(is_tablet)
        try:
            # Wir nutzen Popen statt run, um NICHT zu blockieren
            subprocess.Popen(["qdbus6", DBUS_SHELL, PATH_SHELL, METHOD_JS, js_code],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Auch das Feedback asynchron
            self.show_feedback(is_tablet)
        except Exception as e:
            print(f"[❌] Fehler beim Starten des Switch-Prozesses: {e}")

    def find_device(self):
        """Sucht das Hardware-Device für den Tablet-Switch."""
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            caps = device.capabilities()
            if ecodes.EV_SW in caps and ecodes.SW_TABLET_MODE in caps[ecodes.EV_SW]:
                return device
        return None

    def run(self):
        print("[🚀] Kader42 Event Listener gestartet...")
        
        # Device suchen (mit Retry für langsames Booting)
        device = None
        for _ in range(10):
            device = self.find_device()
            if device: break
            time.sleep(1)

        if not device:
            print("[❌] Kein SW_TABLET_MODE Device gefunden.")
            sys.exit(1)

        # Initialer Hardware-Status abfragen
        try:
            initial_val = device.switches().get(ecodes.SW_TABLET_MODE, 0)
            self.switch_mode(initial_val)
        except: pass

        # Endlos-Überwachung
        for event in device.read_loop():
            if event.type == ecodes.EV_SW and event.code == ecodes.SW_TABLET_MODE:
                self.switch_mode(event.value)

if __name__ == "__main__":
    try:
        Kader42Listener().run()
    except KeyboardInterrupt:
        sys.exit(0)