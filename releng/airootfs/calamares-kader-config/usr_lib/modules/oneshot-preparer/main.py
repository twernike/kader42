import libcalamares
import os
from libcalamares.utils import debug

def run():
    gs = libcalamares.globalstorage
    root = gs.value("rootMountPoint")
    
    # Wir prüfen ALLE möglichen Keys, die Netinstall hinterlassen könnte
    potential_keys = ["packageOperations", "netinstall", "netinstallSelect"]
    all_data = []
    
    for key in potential_keys:
        data = gs.value(key)
        if data:
            debug(f"DEBUG: Daten im Key '{key}' gefunden.")
            all_data = data
            break

    if not all_data:
        debug("DEBUG: Absolut keine Netinstall-Daten gefunden. Keys waren: " + str(gs.keys()))
        return None

    selected_ids = []
    for item in all_data:
        # Extraktion der ID/Name je nach Datenstruktur
        if isinstance(item, str):
            selected_ids.append(item)
        elif isinstance(item, dict):
            # Oft ist es ein Dict mit 'name', 'id' oder 'package'
            val = item.get('id') or item.get('package') or item.get('name')
            if val:
                selected_ids.append(val)

    if selected_ids and root:
        os.makedirs(os.path.join(root, "var/lib/preinstall"), exist_ok=True)
        target = os.path.join(root, "var/lib/preinstall/todo.txt")
        with open(target, "w") as f:
            f.write("\n".join(selected_ids))
        debug(f"SUCCESS: {len(selected_ids)} Pakete für OneShot bereitgelegt.")
    
    return None