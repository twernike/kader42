#!/usr/bin/env python3

import evdev
from evdev import ecodes
import select
import subprocess
import time
import logging

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

SWITCHER = "/usr/bin/plasma-convertible-switcher"

MODE_LAPTOP = 0
MODE_TABLET = 1

POLL_INTERVAL = 0.3

TO_TABLET_DELAY = 2.0
TO_LAPTOP_DELAY = 0.5

DEVICE_RESYNC_INTERVAL = 10


# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[kader42] %(message)s"
)

log = logging.info


# ------------------------------------------------------------
# DEVICE DISCOVERY
# ------------------------------------------------------------

def find_internal_keyboards():
    devices = []

    for path in evdev.list_devices():

        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()

            if ecodes.EV_KEY not in caps:
                continue

            if ecodes.KEY_A not in caps[ecodes.EV_KEY]:
                continue

            name = dev.name.lower()

            if "usb" in name or "bluetooth" in name:
                continue

            devices.append(dev)

        except Exception:
            continue

    return devices


# ------------------------------------------------------------
# DEVICE STATE CHECK
# ------------------------------------------------------------

def device_alive(devices):
    for dev in devices:
        try:
            r, _, _ = select.select([dev.fd], [], [], 0)

            if r:
                for e in dev.read():
                    if e.type == ecodes.EV_KEY:
                        return True

        except Exception:
            continue

    return False


# ------------------------------------------------------------
# SAFE MODE SWITCH
# ------------------------------------------------------------

def set_mode(mode, current_mode):

    # --------------------------------------------------------
    # HARD GUARD (IMPORTANT FOR PRODUCTION)
    # --------------------------------------------------------

    if mode not in (MODE_LAPTOP, MODE_TABLET):
        log(f"IGNORED invalid mode: {mode}")
        return current_mode

    # no change
    if mode == current_mode:
        return current_mode

    try:
        subprocess.run(
            [SWITCHER, str(mode)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

        log("LAPTOP" if mode == MODE_LAPTOP else "TABLET")

    except Exception as e:
        log(f"switch failed: {e}")

    return mode


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    log("kader42 convertible listener started")

    keyboards = find_internal_keyboards()
    last_resync = time.time()

    current_mode = None

    tablet_since = None
    laptop_since = None

    while True:

        now = time.time()

        # periodic rescan (important for suspend/dock)
        if now - last_resync > DEVICE_RESYNC_INTERVAL:
            keyboards = find_internal_keyboards()
            last_resync = now

        alive = device_alive(keyboards)

        # ----------------------------------------------------
        # LAPTOP MODE
        # ----------------------------------------------------

        if alive:
            tablet_since = None

            if laptop_since is None:
                laptop_since = now

            if now - laptop_since > TO_LAPTOP_DELAY:
                current_mode = set_mode(MODE_LAPTOP, current_mode)

        # ----------------------------------------------------
        # TABLET MODE
        # ----------------------------------------------------

        else:
            laptop_since = None

            if tablet_since is None:
                tablet_since = now

            if now - tablet_since > TO_TABLET_DELAY:
                current_mode = set_mode(MODE_TABLET, current_mode)

        time.sleep(POLL_INTERVAL)


# ------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()