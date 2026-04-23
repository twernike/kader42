#!/usr/bin/env python
import evdev
from evdev import ecodes
import subprocess
import time
import sys

def run_switcher(mode):
    """
    Executes the mode change.
    mode 0 = Laptop (hardware returns 0)
    mode 1 = Tablet (hardware returns 1)
    """
    try:
        # We call the switcher directly with the mode value from the hardware
        subprocess.run(["plasma-convertible-switcher", str(mode)], check=True)
        status_text = "NOTEBOOK" if mode == 0 else "TABLET"
        print(f"[✅][kader42-tabletmode-listener] Hardware status detected -> {status_text} (Value: {mode})")
    except Exception as e:
        print(f"[❌][kader42-tabletmode-listener] Error occurred while calling plasma-convertible-switcher: {e}", file=sys.stderr)

def find_tablet_switch_device():
    """
    Scans all input devices for the SW_TABLET_MODE switch.
    """
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        caps = device.capabilities()
        if ecodes.EV_SW in caps:
            if ecodes.SW_TABLET_MODE in caps[ecodes.EV_SW]:
                return device
    return None

def main():
    print("Kader42 Tablet Mode Listener started...")
    
    # Find the device (with a small retry buffer for the boot process)
    device = None
    for i in range(5):
        device = find_tablet_switch_device()
        if device:
            break
        print(f"[🔍][kader42-tabletmode-listener] Searching for Tablet Switch... (Attempt {i+1}/5)")
        time.sleep(2)

    if not device:
        print("[❌][kader42-tabletmode-listener] Critical Error: No SW_TABLET_MODE device found!")
        sys.exit(1)

    print(f"[✅][kader42-tabletmode-listener] Monitoring active on: {device.name} ({device.path})")

    # --- INITIAL CHECK AT STARTUP ---
    # We immediately read the current physical state
    try:
        current_switches = device.switches()
        if ecodes.SW_TABLET_MODE in current_switches:
            initial_val = current_switches[ecodes.SW_TABLET_MODE]
            run_switcher(initial_val)
    except Exception as e:
        print(f"[⚠️][kader42-tabletmode-listener] Warning during initial check: {e}")

    # --- EVENT LOOP ---
    # Here we listen for hardware changes
    for event in device.read_loop():
        if event.type == ecodes.EV_SW and event.code == ecodes.SW_TABLET_MODE:
            # This is where the “logic” takes place:
            # event.value is 0 for a laptop (switch open)
            # event.value is 1 for a tablet (switch closed)
            run_switcher(event.value)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[➜]]\n[kader42-tabletmode-listener] Monitor closed. Exiting gracefully.")
        sys.exit(0)