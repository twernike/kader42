#!/usr/bin/env python3
import evdev
from evdev import ecodes
import select
import time
import subprocess

CHECK_INTERVAL = 1.5
KEY_IDLE = 2.0
STABLE_THRESHOLD = 3

last_mode = None
candidate = None
stable_count = 0


# ---------------- DEVICE FINDER ----------------
def find_devices():
    keyboards = []
    touch = []

    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities()

        # Keyboard heuristic (real input only)
        if ecodes.EV_KEY in caps and ecodes.KEY_A in caps[ecodes.EV_KEY]:
            keyboards.append(dev)

        # Touch detection
        if ecodes.EV_ABS in caps:
            abs_caps = caps[ecodes.EV_ABS]
            if ecodes.ABS_MT_POSITION_X in abs_caps:
                touch.append(dev)

    return keyboards, touch


# ---------------- INPUT ACTIVITY ----------------
def has_input(dev, timeout):
    try:
        r, _, _ = select.select([dev.fd], [], [], timeout)
        if r:
            dev.read()
            return True
    except:
        pass
    return False


def keyboard_used(keyboards):
    return any(has_input(k, KEY_IDLE) for k in keyboards)


def touch_used(touch):
    return any(has_input(t, 0.5) for t in touch)


# ---------------- DECISION ----------------
def decide(kb, tc):
    # hard rule: typing wins always
    if kb:
        return 0  # laptop

    if tc:
        return 1  # tablet

    return 0  # safe default


# ---------------- OUTPUT ----------------
def apply_mode(mode):
    global last_mode

    if mode == last_mode:
        return

    last_mode = mode

    subprocess.run(
        ["plasma-convertible-switcher", str(mode)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("MODE:", "LAPTOP" if mode == 0 else "TABLET")


# ---------------- MAIN LOOP ----------------
def main():
    global candidate, stable_count

    keyboards, touch = find_devices()

    print(f"[INIT] keyboards={len(keyboards)} touch={len(touch)}")

    while True:
        kb = keyboard_used(keyboards)
        tc = touch_used(touch)

        mode = decide(kb, tc)

        # ---------------- STABILITY ----------------
        if mode == candidate:
            stable_count += 1
        else:
            candidate = mode
            stable_count = 0

        if stable_count >= STABLE_THRESHOLD:
            apply_mode(mode)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()