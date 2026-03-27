#!/usr/bin/python3
import libinput
import subprocess
import time

# Pfad zu deinem Switcher-Skript
SWITCHER_SCRIPT = "/usr/bin/plasma-convertible-switcher.sh"
# Zeit in Sekunden, die zwischen zwei Schaltvorgängen liegen MUSS
DEBOUNCE_TIME = 1.5 

last_switch_time = 0

def run_switcher():
    global last_switch_time
    current_time = time.time()
    
    # Prüfen, ob der letzte Schaltvorgang lang genug her ist
    if (current_time - last_switch_time) < DEBOUNCE_TIME:
        print("Prellen (Bounce) erkannt – ignoriere Event.")
        return

    try:
        print("Löse Switcher aus...")
        subprocess.run([SWITCHER_SCRIPT], check=True)
        last_switch_time = current_time
    except Exception as e:
        print(f"Fehler: {e}")

# Setup Libinput via udev für seat0
context = libinput.LibInput(context_type=libinput.ContextType.UDEV)
context.udev_assign_seat("seat0")

print("Maskottchen-Listener: Aktiv (Prellschutz: 1.5s)")

while True:
    context.dispatch() # Events vom Kernel abholen
    for event in context.get_event():
        # Wir prüfen auf den Event-Typ 'SWITCH_TOGGLE'
        if event.type.name == "SWITCH_TOGGLE":
            run_switcher()
    
    # Ein winziger Sleep in der Schleife schont die CPU, 
    # falls dispatch() mal nicht blockiert
    time.sleep(0.1)