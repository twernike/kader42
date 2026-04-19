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
    Try setting this mode. If `retry=True`, the script will attempt the login 
    up to 5 times in quick succession. 
    This is useful during the boot process when the system might not be fully ready to handle the switch immediately.
    """
    for i in range(5 if retry else 1):
        try:
            subprocess.run(["plasma-convertible-switcher", str(mode)], check=True)
            return True # Erfolg!
        except Exception:
            if retry:
                time.sleep(0.5) # Just a brief moment of silence during system startup
            else:
                break
    return False
    # try:
    #     # We call the switcher directly with the mode value from the hardware
    #     subprocess.run(["plasma-convertible-switcher", str(mode)], check=True)
    #     status_text = "NOTEBOOK" if mode == 0 else "TABLET"
    #     print(f"[kader42-tabletmode-listener] Hardware status detected -> {status_text} (Value: {mode})")
    # except Exception as e:
    #     print(f"[kader42-tabletmode-listener] Error occurred while calling plasma-convertible-switcher: {e}", file=sys.stderr)

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
    # 1. Find a device with the SW_TABLET_MODE switch (this is the hardware event we want to monitor)
    device = None
    # Quick check at startup to see if the device is already connected (search takes max. 2 seconds)
    for _ in range(4):
        device = find_tablet_switch_device()
        if device:
            break
        time.sleep(0.5)

    if not device:
        print("[kader42-tabletmode-listener] No tablet switch found. Quitting.")
        sys.exit(0) # Beenden ohne Fehler, falls Hardware kein Convertible ist

    # 2. Set initial status immediately upon login
    # We use `retry=True` to intercept the moment the desktop is being built
    try:
        initial_val = device.switches().get(ecodes.SW_TABLET_MODE, 0)
        run_switcher(initial_val, retry=True)
    except Exception as e:
        print(f"[kader42-tabletmode-listener] Initial check failed: {e}")

    # 3. Continuous monitoring of hardware events
    # read_loop() is extremely CPU-efficient (waits for interrupts)
    for event in device.read_loop():
        if event.type == ecodes.EV_SW and event.code == ecodes.SW_TABLET_MODE:
            # 0 = Notebook, 1 = Tablet
            run_switcher(event.value)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[kader42-tabletmode-listener] Monitor closed. Exiting gracefully.")
        sys.exit(0)