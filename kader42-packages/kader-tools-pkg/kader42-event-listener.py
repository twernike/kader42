#!/usr/bin/env python3
import evdev
from evdev import ecodes
import subprocess
import time
import sys
import threading
import os
import dbus
import dbus.mainloop.glib

# ---------------- CONFIG ----------------
USE_DBUS_FALLBACK = True
USE_KEYBOARD_FALLBACK = True

# ---------------- STATE ----------------
last_state = None
state_source = None  # "hw", "kbd", "dbus"

# ---------------- CORE ----------------
def run_switcher(mode, source):
    global last_state, state_source

    if last_state == mode:
        return

    last_state = mode
    state_source = source

    try:
        subprocess.run(["plasma-convertible-switcher", str(mode)], check=True)
        status = "NOTEBOOK" if mode == 0 else "TABLET"
        print(f"[{source}] → {status}")
    except Exception as e:
        print(f"[ERROR] switcher failed: {e}", file=sys.stderr)


# ---------------- HW SWITCH ----------------
def find_tablet_switch_device():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        caps = device.capabilities()
        if ecodes.EV_SW in caps:
            if ecodes.SW_TABLET_MODE in caps[ecodes.EV_SW]:
                return device
    return None


def hw_listener():
    device = None

    for i in range(5):
        device = find_tablet_switch_device()
        if device:
            break
        time.sleep(2)

    if not device:
        print("[WARN] No HW switch found, falling back")
        return False

    print(f"[HW] Listening on {device.path}")

    # initial state
    try:
        switches = device.switches()
        if ecodes.SW_TABLET_MODE in switches:
            run_switcher(switches[ecodes.SW_TABLET_MODE], "hw-init")
    except:
        pass

    for event in device.read_loop():
        if event.type == ecodes.EV_SW and event.code == ecodes.SW_TABLET_MODE:
            run_switcher(event.value, "hw")

    return True


# ---------------- KEYBOARD FALLBACK ----------------
def keyboard_fallback():
    # very generic heuristic placeholder
    # (you can later refine per device)
    try:
        while True:
            kb_present = os.path.exists("/dev/input/by-path")
            # simple heuristic: not real detection yet
            time.sleep(5)
    except:
        pass


# ---------------- DBUS FALLBACK ----------------
def dbus_listener():
    from gi.repository import GLib

    def handler(*args, **kwargs):
        try:
            value = args[0] if args else None
            if value is True:
                run_switcher(1, "dbus")
            elif value is False:
                run_switcher(0, "dbus")
        except:
            pass

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    bus.add_signal_receiver(
        handler,
        signal_name="tabletModeChanged",
        dbus_interface="org.kde.KWin",
        path="/org/kde/KWin"
    )

    loop = GLib.MainLoop()
    print("[DBUS] Fallback active")
    loop.run()


# ---------------- MAIN ----------------
def main():
    print("Kader42 Convertible Listener starting...")

    # 1. HW first (PRIMARY)
    if hw_listener():
        return

    # 2. DBus fallback
    if USE_DBUS_FALLBACK:
        print("[INFO] Starting DBus fallback")
        dbus_listener()
    else:
        print("[ERROR] No valid input source found")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)