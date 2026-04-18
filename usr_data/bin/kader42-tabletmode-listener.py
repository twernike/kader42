#!/usr/bin/env python
import subprocess
import sys

def run_switcher(mode):
    """
    Calls the plasma-convertible-switcher.
    1 = Tablet mode (keyboard disabled)
    0 = Notebook mode (keyboard enabled)
    """
    try:
        # Wir nutzen volle Pfade für den Service-Betrieb
        subprocess.run(["/usr/local/bin/plasma-convertible-switcher", str(mode)], check=True)
        print(f"[✅][kader42-tablet-mode-listener] Mode set to {'TABLET' if mode == 1 else 'NOTEBOOK'}.")
    except Exception as e:
        print(f"[❌][kader42-tablet-mode-listener] Error calling the switcher: {e}", file=sys.stderr)

def get_initial_state():
    """
    Checks the current hardware status when the service starts.
    """
    try:
        output = subprocess.check_output(["libinput", "list-devices"], text=True)
        # We are looking for the Tablet Mode Switch and its status
        if "switch tablet-mode" in output.lower():
            # If ‘state: down’ or ‘state: set’ (depending on the libinput version)
            # Here we simply check for the presence of 'state: set'
            if "state: set" in output.lower():
                return 1
    except Exception:
        print("[❌][kader42-tablet-mode-listener] Error checking initial state.", file=sys.stderr)
    return 0

def monitor_logic():
    """
    The main loop: Sets the initial value and then listens for events.
    """
    print("Kader⁴² Tablet Mode Listener started...")

    #  1. Initial check during bootup
    initial_mode = get_initial_state()
    run_switcher(initial_mode)

    # 2. Event monitoring via libinput
    # We use --screen-stdout to ensure that we receive the lines immediately
    try:
        process = subprocess.Popen(
            ["libinput", "debug-events"], 
            stdout=subprocess.PIPE, 
            text=True,
            bufsize=1 # Line-buffered für Echtzeit-Reaktion
        )
    except FileNotFoundError:
        print("[❌][kader42-tablet-mode-listener] Error: 'libinput' is not installed! Please install the libinput package via pacman, first!", file=sys.stderr)
        return

    for line in iter(process.stdout.readline, ""):
        # We are looking for the hardware event for the tablet mode
        if "switch tablet-mode" in line:
            if "state 1" in line:
                run_switcher(1)
            elif "state 0" in line:
                run_switcher(0)

if __name__ == "__main__":
    try:
        monitor_logic()
    except KeyboardInterrupt:
        print("\nKader⁴² Tablet Mode Listener stopped.")
        sys.exit(0)