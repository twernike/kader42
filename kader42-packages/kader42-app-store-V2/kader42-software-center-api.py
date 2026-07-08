#!/usr/bin/usr/env python
# /usr/lib/kader-store/api.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import sqlite3
import os
import subprocess
from shared import DB_PATH, CACHE_DIR, init_environment

# Here we define the categories and which search terms or 
# Arch package groups should be queried in the background.
CATEGORY_DEFINITIONS = [
    {"id": "development", "icon":"applications-development","de": "Entwicklungstools", "en": "Development", "query": "code visual-studio-code-bin vscodium-bin eclipse pycharm gitkraken"},
    {"id": "internet","icon": "applications-internet", "de": "Internet & Browser", "en": "Internet", "query": "firefox chromium thunderbird filezilla discord"},
    {"id": "multimedia", "icon": "applications-multimedia","de": "Multimedia", "en": "Multimedia", "query": "vlc gimp inkscape blender audacity handbrake"},
    {"id": "office", "icon": "applications-office", "de": "Büro & Office", "en": "Office", "query": "libreoffice-fresh openboard xournalpp"}
]

# Instead of writing `server = HTTPServer(...)` directly, let's make it reusable:
class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


SETTINGS_DIR = os.path.expanduser("~/.config/kader42")
SETTINGS_FILE = f"{SETTINGS_DIR}/software-center.json"

import subprocess
import os
import json

SETTINGS_DIR = "/etc/kader42"
SETTINGS_FILE = f"{SETTINGS_DIR}/software-center.json"

def get_systemd_timer_state():
    """Checks in real time within the system whether the systemd timer is permanently enabled."""
    try:
        res = subprocess.run("systemctl is-enabled kader42-autoupdate.timer", shell=True, capture_output=True, text=True)
        # If the timer is enabled, `systemctl` returns exactly “enabled”
        return res.stdout.strip() == "enabled"
    except:
        return False

def load_settings():
    """Retrieve the activation status in real time via `is-enabled` and the time from the JSON."""
    saved_time = "04:00"
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                saved_time = data.get("update_time", "04:00")
        except Exception as e:
            print(f"Fehler beim Laden der JSON: {e}")
        
    # If the file doesn't exist or was corrupted, 
    # we'll still return the correct structure!
    return {
        "auto_updates": get_systemd_timer_state(),
        "update_time": saved_time
    }

def save_settings(data):
    """Write the JSON and run the actual `systemctl enable/disable` commands."""
    try:
        auto_updates = data.get("auto_updates", False)
        update_time = data.get("update_time", "04:00")

        # 1. Save only the time in the JSON (if needed, e.g., for overrides)
        if not os.path.exists(SETTINGS_DIR):
            try:
                os.makedirs(SETTINGS_DIR, exist_ok=True)
            except PermissionError:
                # If the API doesn't have permissions here, the helper script/Polkit handles it
                pass
                
        if auto_updates:
            # 2. Permanently enable or disable the systemd timer using pkexec
            subprocess.run("pkexec systemctl enable --now kader42-autoupdate.timer", shell=True)
            print("[kader42-software-center-api] ➔ systemd: systemctl enable --now kader42-autoupdate.timer executed.")
        else:
            # Deletes the symlinks and stops the timer immediately (--now)
            subprocess.run("pkexec systemctl disable --now kader42-autoupdate.timer", shell=True)
            print("[kader42-software-center-api] ➔ systemd: systemctl disable --now kader42-autoupdate.timer executed")
            
        # Optional: Here we write the JSON (if Polkit rules apply to the directory)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"update_time": update_time}, f, indent=4)
            
    except Exception as e:
        print(f"[kader42-software-center-api] Error while running systemctl: {e}")

class StoreAPIHandler(BaseHTTPRequestHandler):
    

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        path_str = url_parts.path
        
        # 1. ENDPOINT: Kategorien abrufen
        if path_str == "/categories":
            self._set_headers(200)
            self.wfile.write(json.dumps(CATEGORY_DEFINITIONS).encode('utf-8'))

        # 2. ENDPOINT: Apps einer Kategorie ODER freie Suche
        elif path_str == "/apps":
            search_term = ""
            if "category" in query_params:
                cat_id = query_params["category"][0]
                cat = next((c for c in CATEGORY_DEFINITIONS if c["id"] == cat_id), None)
                if cat:
                    search_term = cat["query"]
            elif "search" in query_params:
                search_term = query_params["search"][0]
                
            if search_term:
                results = self.search_via_yay(search_term)
                self._set_headers(200)
                self.wfile.write(json.dumps(results).encode('utf-8'))
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps([]).encode('utf-8'))

        # 3. ENDPOINT: View Installed Apps & Updates
        elif path_str == "/installed":
            results = self.get_installed_apps_and_updates()
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))

        elif path_str == "/updates":
            all_apps = self.get_installed_apps_and_updates()
            
            # We filter exactly by the status string!
            update_packages = [app for app in all_apps if app.get('status') == 'update_available']
            
            results = {
                "total_updates": len(update_packages),
                "packages": update_packages
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))
        elif path_str == "/settings":
            settings_data = load_settings()
            response_bytes = json.dumps(settings_data).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)

        # ==========================================================
        # Check Job Status (/job/<id>)
        # ==========================================================
        elif path_str.startswith("/job/"):
            try:
                # Schneidet das "/job/" ab, um die ID als Zahl zu bekommen
                job_id_str = path_str.split("/")[-1]
                job_id = int(job_id_str)
                
                # Trim off “/job/” to get the ID as a number
                status_data = self.get_job_status(job_id)
                
                self._set_headers(200)
                self.wfile.write(json.dumps(status_data).encode('utf-8'))
            except Exception as e:
                print(f"API Fehler beim Job-Polling: {e}")
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid Job ID"}).encode('utf-8'))
                
        # ==========================================================
        # FALLBACK: Prevents 0-byte responses for unknown paths
        # ==========================================================
        else:
            print(f"⚠️[kader42-software-center-api] Unknown GET path called: {path_str}")
            fallback_bytes = b"{}"
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(fallback_bytes)))
            self.end_headers()
            self.wfile.write(fallback_bytes)

    def do_POST(self):
        if self.path == "/job":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            post_data = json.loads(body)
            
            pkg_name = post_data.get("package_name")
            source = post_data.get("source", "repo")
            action = post_data.get("action")
            
            if not pkg_name or not action:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing parameters"}).encode('utf-8'))
                return
                
            job_id = self.queue_job(pkg_name, source, action)
            self._set_headers(201)
            self.wfile.write(json.dumps({"id": job_id, "status": "queued"}).encode('utf-8'))
        elif self.path == "/settings":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            settings_data = json.loads(body)
            save_settings(settings_data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "saved"}).encode('utf-8'))

    def search_via_yay(self, query):
        apps_found = []
        query = query.strip().lower()
        if not query:
            return []

        installed_packages = set()
        updates_available = set()
        try:
            if os.path.exists("/var/lib/pacman/local"):
                for d in os.listdir("/var/lib/pacman/local"):
                    if not d or "-" not in d: continue
                    
                    # A local Pacman folder always looks like this: pkgname-version-release
                    # We split it from the right and remove the last two elements (version & release).
                    parts = d.split("-")
                    if len(parts) > 2:
                        # Connect all parts except the last two with a hyphen
                        pkg_name = "-".join(parts[:-2])
                        installed_packages.add(pkg_name)

            res_upd = subprocess.run("yay -Qu", shell=True, capture_output=True, text=True)
            for line in res_upd.stdout.split("\n"):
                if line.strip():
                    updates_available.add(line.split(" ")[0].strip())
        except Exception as e:
            print(f"[kader42-software-center-api] API Search Preprocessing Error: {e}")

        # 2. FILTER: CATEGORY (Exact Package List) vs. FREE SEARCH
        # We check whether the query comes from the CATEGORY_DEFINITIONS
        is_category = any(c["query"] == query for c in CATEGORY_DEFINITIONS) or " " in query

        if is_category:
            # For categories, we query the exact packages directly via info (-Si)ab
            package_list = query.split()
            # To avoid overloading the AUR, we use pacman/yay efficiently
            cmd = f"yay -Si {' '.join(package_list)}"
        else:
            # For the free search, we continue to use the regular search (-Ss)
            cmd = f"yay -Ss {query}"
        
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = res.stdout.split("\n")
            
            current_pkg = None
            
            if is_category:
                # PARSER FÜR 'yay -Si' (Kategorien)
                repo = "repo"  # Safe fallback value initialized in advance!
                
                for line in lines:
                    line_stripped = line.strip()
                    if not line_stripped: continue
                    
                    # Detects repository or database (whether DE or EN)
                    if any(line_stripped.startswith(x) for x in ["Repository", "Datenbank", "Database"]):
                        repo = line_stripped.split(":")[-1].strip()
                        
                    elif any(line_stripped.startswith(x) for x in ["Name", "Package Name"]):
                        pkg_name = line_stripped.split(":")[-1].strip()
                        source_type = "aur" if repo.lower() == "aur" else "repo"
                        
                        current_pkg = {
                            "package_name": pkg_name,
                            "name": pkg_name.replace("-bin", "").replace("-git", "").capitalize(),
                            "source": source_type,
                            "description": ""
                        }
                        
                    elif any(line_stripped.startswith(x) for x in ["Beschreibung", "Description"]):
                        if current_pkg:
                            current_pkg["description"] = line_stripped.split(":")[-1].strip()
                            p_name = current_pkg["package_name"]
                            
                            # Status zuweisen
                            if p_name in updates_available:
                                current_pkg["status"] = "update_available"
                            elif p_name in installed_packages:
                                current_pkg["status"] = "installed"
                            else:
                                current_pkg["status"] = "available"
                            
                            # Core-Token zuweisen
                            core_descriptions = {
                                "code": "desc_core_code", "visual-studio-code-bin": "desc_core_vscode_bin",
                                "vscodium-bin": "desc_core_vscodium", "firefox": "desc_core_firefox",
                                "chromium": "desc_core_chromium", "gimp": "desc_core_gimp",
                                "vlc": "desc_core_vlc", "libreoffice-fresh": "desc_core_libreoffice",
                                "openboard": "desc_core_openboard"
                            }
                            if p_name in core_descriptions:
                                current_pkg["description"] = core_descriptions[p_name]
                            else:
                                current_pkg["description"] = "desc_generic_system"

                            apps_found.append(current_pkg)
                            current_pkg = None
                            repo = "repo" # Reset for the next item in the list
            else:
                # PARSER FOR ‘yay -Ss’ (Free search - remains the same)
                for line in lines:
                    line_stripped = line.strip()
                    if not line_stripped: continue
                    
                    if "/" in line_stripped and not line_stripped.startswith("http"):
                        try:
                            parts = line_stripped.split("/")
                            repo = parts[0].strip()
                            pkg_name = parts[1].split(" ")[0].strip()
                            source_type = "aur" if repo.lower() == "aur" else "repo"
                            
                            current_pkg = {
                                "package_name": pkg_name,
                                "name": pkg_name.replace("-bin", "").replace("-git", "").capitalize(),
                                "source": source_type,
                                "description": ""
                            }
                        except:
                            current_pkg = None
                    
                    elif current_pkg and not line_stripped.startswith("    "):
                        current_pkg["description"] = line_stripped
                        p_name = current_pkg["package_name"]

                        if p_name.lower() == "kader42-software-center":
                            current_pkg = None
                            continue
                        
                        if p_name in updates_available:
                            current_pkg["status"] = "update_available"
                        elif p_name in installed_packages:
                            current_pkg["status"] = "installed"
                        else:
                            current_pkg["status"] = "available"
                        
                        core_descriptions = {
                            "code": "desc_core_code", "visual-studio-code-bin": "desc_core_vscode_bin",
                            "vscodium-bin": "desc_core_vscodium", "firefox": "desc_core_firefox",
                            "chromium": "desc_core_chromium", "gimp": "desc_core_gimp",
                            "vlc": "desc_core_vlc", "libreoffice-fresh": "desc_core_libreoffice",
                            "openboard": "desc_core_openboard"
                        }
                        if p_name in core_descriptions:
                            current_pkg["description"] = core_descriptions[p_name]

                        apps_found.append(current_pkg)
                        current_pkg = None
                        
                    if len(apps_found) >= 15:
                        break
                        
            return apps_found
        except Exception as e:
            print(f"Fehler bei API-Suche: {e}")
            return []
    
    def queue_job(self, pkg_name, source, action):
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO jobs (package_name, source, action) VALUES (?, ?, ?)", (pkg_name, source, action))
            conn.commit()
            return cursor.lastrowid

    def get_job_status(self, job_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT status, progress FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if row: return {"status": row["status"], "progress": row["progress"]}
            return {"status": "unknown", "progress": 0}
    
    def get_installed_apps_and_updates(self):
        apps = []
        
        # 1. Get all explicitly installed packages
        try:
            # shell=True ensures that yay runs in the usual user environment
            res_installed = subprocess.run("yay -Qe", shell=True, capture_output=True, text=True)
            
            if res_installed.returncode != 0:
                print(f"STDOUT von yay -Qe: {res_installed.stdout}")
                print(f"STDERR von yay -Qe: {res_installed.stderr}")
                return []
                
            explicit_packages = set()
            for line in res_installed.stdout.split("\n"):
                if line.strip():
                    pkg_name = line.split(" ")[0].strip()
                    explicit_packages.add(pkg_name)
        except Exception as e:
            print(f"API Exception bei yay -Qe: {e}")
            return []

        # 2.  Check for all available updates (Repo + AUR combined)
        updates_available = set()
        try:
            res_updates = subprocess.run("yay -Qu", shell=True, capture_output=True, text=True)
            for line in res_updates.stdout.split("\n"):
                if line.strip():
                    updates_available.add(line.split(" ")[0].strip())
        except Exception:
            pass

        # 3. List all installed AUR packages
        try:
            res_aur = subprocess.run("yay -Qm", shell=True, capture_output=True, text=True)
            aur_packages = {line.split(" ")[0].strip() for line in res_aur.stdout.split("\n") if line.strip()}
        except Exception:
            aur_packages = set()

        # 4. Filter by GUI applications using the .desktop filename heuristic
        desktop_apps = set()
        desktop_dir = "/usr/share/applications"
        if os.path.exists(desktop_dir):
            for f in os.listdir(desktop_dir):
                if f.endswith(".desktop"):
                    base_name = f.replace(".desktop", "").lower()
                    
                    for pkg in explicit_packages:
                        if pkg in base_name or base_name in pkg:
                            desktop_apps.add(pkg)

        # Security fallback for well-known core apps in your distribution
        known_guis = ["code", "visual-studio-code-bin", "vscodium-bin", "discord", "steam", "spotify"]
        for pkg in known_guis:
            if pkg in explicit_packages:
                desktop_apps.add(pkg)

        # 5. Building a JSON Structure for the Front End
        for pkg in desktop_apps:
            has_update = pkg in updates_available
            source_type = "aur" if pkg in aur_packages else "repo"
            status_type = "update_available" if has_update else "installed"
            
            # Instead of hard-coded text, we send variables to the front end
            if has_update:
                desc_key = "desc_update_available"
            else:
                desc_key = "desc_installed_repo" if source_type == "repo" else "desc_installed_aur"

            apps.append({
                "name": pkg.replace("-bin", "").replace("-git", "").capitalize(),
                "package_name": pkg,
                "description": desc_key, # This is where the key goes!
                "source": source_type,
                "status": status_type,
                "icon_path": "/usr/share/pixmaps/nobody.png"
            })
            
        apps.sort(key=lambda x: x["status"] != "update_available")
        return apps

if __name__ == "__main__":
    init_environment()
    print("Starting Kader⁴² App Store REST API on http://127.0.0.1:8080 ...")
    server = ReusableHTTPServer(('127.0.0.1', 8080), StoreAPIHandler)
    server.serve_forever()