#!/usr/bin/env python
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

class SystemdHTTPServer(HTTPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        # When starting up, systemd sets the LISTEN_FDS environment variable via a .socket file
        listen_fds = int(os.environ.get("LISTEN_FDS", 0))

        if listen_fds > 0:
            # ➔ SYSTEMD SOCKET ACTIVATION MODE
            # Creates the object without attempting to bind to a socket
            super().__init__(server_address, RequestHandlerClass, bind_and_activate=False)
            
            # Closes the dummy socket created by TCPServer
            if hasattr(self, "socket") and self.socket:
                self.socket.close()

            # Takes over the socket (file descriptor 3) already opened by systemd
            self.socket = socket.socket(fileno=3)
            self.server_address = self.socket.getsockname()
            print("[kader42-software-center-api] Systemd Socket Activation detected and applied.")
        else:
            # ➔ STANDALONE MODE (e.g., manual startup in the terminal)
            super().__init__(server_address, RequestHandlerClass, bind_and_activate=True)


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

# In load_settings() und save_settings() die neuen Keys ergänzen:
def load_settings():
    saved_time = "04:00"
    retention_completed = 1
    retention_failed = 3
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                saved_time = data.get("update_time", "04:00")
                retention_completed = data.get("retention_completed_days", 1)
                retention_failed = data.get("retention_failed_days", 3)
        except Exception as e:
            print(f"Fehler beim Laden der JSON: {e}")
        
    return {
        "auto_updates": get_systemd_timer_state(),
        "update_time": saved_time,
        "retention_completed_days": retention_completed,
        "retention_failed_days": retention_failed
    }

def save_settings(data):
    try:
        auto_updates = data.get("auto_updates", False)
        update_time = data.get("update_time", "04:00")
        retention_completed = int(data.get("retention_completed_days", 1))
        retention_failed = int(data.get("retention_failed_days", 3))

        if auto_updates:
            subprocess.run("pkexec systemctl enable --now kader42-autoupdate.timer", shell=True)
        else:
            subprocess.run("pkexec systemctl disable --now kader42-autoupdate.timer", shell=True)
            
        with open(SETTINGS_FILE, "w") as f:
            json.dump({
                "update_time": update_time,
                "retention_completed_days": retention_completed,
                "retention_failed_days": retention_failed
            }, f, indent=4)
            
    except Exception as e:
        print(f"Error while saving settings: {e}")

class StoreAPIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        """Sends JSON data with the correct Content-Length to the client."""
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def get_job_log(self, job_id):
        """Reads only the log output of a job from the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT log_output FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else ""

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        path_str = url_parts.path
        
        # Automatic Update Check for the Software Center
        if path_str == "/self-update-check":
            has_update = False
            try:
                res = subprocess.run("yay -Qu kader42-software-center", shell=True, capture_output=True, text=True)
                if res.stdout.strip():
                    has_update = True
            except Exception:
                pass
            self.send_json({"update_available": has_update, "package_name": "kader42-software-center"})
            return
        
        elif path_str == "/categories":
            self.send_json(CATEGORY_DEFINITIONS)

        elif path_str == "/apps":
            search_term = ""
            if "category" in query_params:
                cat_id = query_params["category"][0]
                cat = next((c for c in CATEGORY_DEFINITIONS if c["id"] == cat_id), None)
                if cat: search_term = cat["query"]
            elif "search" in query_params:
                search_term = query_params["search"][0]
                
            results = self.search_via_yay(search_term) if search_term else []
            self.send_json(results)

        elif path_str == "/installed":
            results = self.get_installed_apps_and_updates()
            self.send_json(results)

        elif path_str == "/updates":
            all_apps = self.get_installed_apps_and_updates()
            update_packages = [app for app in all_apps if app.get('status') == 'update_available']
            self.send_json({"total_updates": len(update_packages), "packages": update_packages})

        elif path_str == "/settings":
            settings_data = load_settings()
            self.send_json(settings_data)
            

        elif path_str.startswith("/job/") and path_str.endswith("/log"):
            try:
                # Extracts the ID from /job/42/log
                job_id = int(path_str.split("/")[2])
                log_text = self.get_job_log(job_id)
                self.send_json({"id": job_id, "log": log_text})
            except Exception as e:
                print(f"API Log-Fetch Error: {e}")
                self.send_json({"error": "Invalid Job ID"}, 400)

        elif path_str.startswith("/job/"):
            try:
                job_id_str = path_str.split("/")[-1]
                job_id = int(job_id_str)
                status_data = self.get_job_status(job_id)
                # IMPORTANT: Respond now using `send_json`, including `Content-Length`!
                self.send_json(status_data)
            except Exception as e:
                print(f"API Error During Job Polling: {e}")
                self.send_json({"error": "Invalid Job ID"}, 400)

        elif path_str == "/jobs":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, package_name, action, status, progress, log_output, created_at 
                    FROM jobs ORDER BY id DESC LIMIT 50
                """)
                rows = cursor.fetchall()
                jobs = [dict(row) for row in rows]
                self.send_json(jobs)
            return
        

    def do_POST(self):
        if self.path == "/job":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            post_data = json.loads(body)
            
            pkg_name = post_data.get("package_name")
            source = post_data.get("source", "repo")
            action = post_data.get("action")
            
            if not pkg_name or not action:
                err_bytes = json.dumps({"error": "Missing parameters"}).encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(err_bytes)))
                self.end_headers()
                self.wfile.write(err_bytes)
                return
                
            job_id = self.queue_job(pkg_name, source, action)
            
            # IMPORTANT: Respond with an explicit `Content-Length` for PySide6!
            res_bytes = json.dumps({"id": job_id, "status": "queued"}).encode('utf-8')
            
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(res_bytes)))
            self.end_headers()
            self.wfile.write(res_bytes)

        elif self.path == "/settings":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            settings_data = json.loads(body)
            save_settings(settings_data)
            
            res_bytes = json.dumps({"status": "saved"}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(res_bytes)))
            self.end_headers()
            self.wfile.write(res_bytes)

    def do_DELETE(self):
        # NEW: Manually delete individual jobs
        path_str = self.path
        if path_str.startswith("/job/"):
            try:
                job_id = int(path_str.split("/")[-1])
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
                    conn.commit()
                self.send_json({"status": "deleted", "id": job_id})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)

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
                            
                            # Assign Status
                            if p_name in updates_available:
                                current_pkg["status"] = "update_available"
                            elif p_name in installed_packages:
                                current_pkg["status"] = "installed"
                            else:
                                current_pkg["status"] = "available"
                            
                            # Assign Core Tokens
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
                # PARSER FOR “yay -Ss” (Free search)
                for raw_line in lines:
                    if not raw_line.strip():
                        continue
                    
                    # 1. Lines without leading spaces = package name + repoo
                    if not raw_line.startswith(" ") and "/" in raw_line:
                        if current_pkg:
                            apps_found.append(current_pkg)
                            current_pkg = None

                        try:
                            line_stripped = raw_line.strip()
                            parts = line_stripped.split("/")
                            repo = parts[0].strip()
                            pkg_name = parts[1].split(" ")[0].strip()
                            
                            if pkg_name.lower() == "kader42-software-center":
                                continue

                            source_type = "aur" if repo.lower() == "aur" else "repo"
                            
                            current_pkg = {
                                "package_name": pkg_name,
                                "name": pkg_name.replace("-bin", "").replace("-git", "").capitalize(),
                                "source": source_type,
                                "description": ""
                            }
                        except Exception:
                            current_pkg = None
                    
                    # 2. Indented lines = description
                    elif raw_line.startswith(" ") and current_pkg:
                        current_pkg["description"] = raw_line.strip()
                        p_name = current_pkg["package_name"]

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

                # Save the last object if the output ends without a subsequent line
                if current_pkg:
                    apps_found.append(current_pkg)

                #Sort exact matches such as ‘davinci-resolve’ to the top
                apps_found.sort(
                    key=lambda x: (
                        0 if x["package_name"].lower() == query else 1,
                        0 if x["package_name"].lower().startswith(query) else 1
                    )
                )

                # After the LOOP LIMIT AND RETURN
                if len(query) <= 3:
                    return apps_found[:20]
                else:
                    return apps_found[:100]
            
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
            cursor.execute("SELECT status, progress, log_output FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if row: 
                return {
                    "status": row["status"], 
                    "progress": row["progress"], 
                    "log": row["log_output"] if row["log_output"] else ""
            }
        return {"status": "unknown", "progress": 0, "log": ""}

    def get_all_jobs(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""SELECT id, package_name, action, status, progress, log_output, created_at 
                    FROM jobs ORDER BY id DESC LIMIT 50""")
            rows = cursor.fetchall()
            jobs = [dict(row) for row in rows]
            self.send_json(jobs)
    
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
    print("Started Kader⁴² App Store REST API on http://127.0.0.1:8080 ...")
    # server = ReusableHTTPServer(('127.0.0.1', 8080), StoreAPIHandler)
    server = SystemdHTTPServer(('127.0.0.1', 8080), StoreAPIHandler)
    server.serve_forever()