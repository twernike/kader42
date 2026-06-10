# /usr/lib/kader-store/api.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import sqlite3
import os
import subprocess
from shared import DB_PATH, CACHE_DIR, init_environment

# Hier definieren wir die Kategorien und welche Suchbegriffe oder 
# Arch-Paketgruppen im Hintergrund abgefragt werden sollen.
CATEGORY_DEFINITIONS = [
    {"id": "development", "icon":"applications-development","de": "Entwicklungstools", "en": "Development", "query": "code visual-studio-code-bin vscodium-bin eclipse pycharm gitkraken"},
    {"id": "internet","icon": "applications-internet", "de": "Internet & Browser", "en": "Internet", "query": "firefox chromium thunderbird filezilla discord"},
    {"id": "multimedia", "icon": "applications-multimedia","de": "Multimedia", "en": "Multimedia", "query": "vlc gimp inkscape blender audacity handbrake"},
    {"id": "office", "icon": "applications-office", "de": "Büro & Office", "en": "Office", "query": "libreoffice-fresh openboard xournalpp"}
]

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

        # 3. ENDPOINT: Installierte Apps & Updates abrufen
        elif path_str == "/installed":
            results = self.get_installed_apps_and_updates()
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))

        # ==========================================================
        # NEU: HIER WAR DAS LOCH! ENDPOINT: Job-Status abfragen (/job/<id>)
        # ==========================================================
        elif path_str.startswith("/job/"):
            try:
                # Schneidet das "/job/" ab, um die ID als Zahl zu bekommen
                job_id_str = path_str.split("/")[-1]
                job_id = int(job_id_str)
                
                # Holt den Status direkt aus der SQLite-Datenbank
                status_data = self.get_job_status(job_id)
                
                self._set_headers(200)
                self.wfile.write(json.dumps(status_data).encode('utf-8'))
            except Exception as e:
                print(f"API Fehler beim Job-Polling: {e}")
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid Job ID"}).encode('utf-8'))

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

    def search_via_yay(self, query):
        apps_found = []
        query = query.strip().lower()
        if not query:
            return []

        # 1. ROBUSTER LOKALER STATUS-CACHE (Allgemeingültig für Arch Linux)
        installed_packages = set()
        updates_available = set()
        try:
            if os.path.exists("/var/lib/pacman/local"):
                for d in os.listdir("/var/lib/pacman/local"):
                    if not d or "-" not in d: continue
                    
                    # Arch-Ordner-Logik: [paketname]-[version]-[release]
                    # Wir gehen von hinten durch den Ordnernamen, um den Start der Version zu finden
                    parts = d.split("-")
                    # Die Version beginnt im Regelfall mit einer Zahl (z.B. "126.0")
                    # Wir suchen das erste Element von hinten, das mit einer Ziffer startet
                    for i in range(len(parts) - 1, 0, -1):
                        if parts[i] and parts[i][0].isdigit():
                            # Alles vor diesem Element ist der echte Paketname!
                            pkg_name = "-".join(parts[:i])
                            installed_packages.add(pkg_name)
                            break

            # Updates via yay holen
            res_upd = subprocess.run("yay -Qu", shell=True, capture_output=True, text=True)
            for line in res_upd.stdout.split("\n"):
                if line.strip():
                    updates_available.add(line.split(" ")[0].strip())
        except Exception as e:
            print(f"API Such-Vorbehandlung Fehler: {e}")

        # 2. SUCHE AUSFÜHREN
        is_category = " " in query
        cmd = f"yay -Ss {query}" if not is_category else f"yay -Ss {' '.join(query.split())}"
        
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = res.stdout.split("\n")
            
            current_pkg = None
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
                    
                    # Status-Zuweisung greift jetzt perfekt auf das Set zu!
                    if p_name in updates_available:
                        current_pkg["status"] = "update_available"
                    elif p_name in installed_packages:
                        current_pkg["status"] = "installed"
                    else:
                        current_pkg["status"] = "available"
                    
                    # Core-Beschreibungen (Token)
                    core_descriptions = {
                        "code": "desc_core_code", "visual-studio-code-bin": "desc_core_vscode_bin",
                        "vscodium-bin": "desc_core_vscodium", "firefox": "desc_core_firefox",
                        "chromium": "desc_core_chromium", "gimp": "desc_core_gimp",
                        "vlc": "desc_core_vlc", "libreoffice-fresh": "desc_core_libreoffice",
                        "openboard": "desc_core_openboard"
                    }
                    if p_name in core_descriptions:
                        current_pkg["description"] = core_descriptions[p_name]
                    elif is_category:
                        current_pkg["description"] = "desc_generic_system"

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
        
        # 1. Alle explizit installierten Pakete holen
        try:
            # shell=True sorgt dafür, dass yay in deiner gewohnten Benutzerumgebung ausgeführt wird
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

        # 2. Alle verfügbaren Updates ermitteln (Repo + AUR kombiniert)
        updates_available = set()
        try:
            res_updates = subprocess.run("yay -Qu", shell=True, capture_output=True, text=True)
            for line in res_updates.stdout.split("\n"):
                if line.strip():
                    updates_available.add(line.split(" ")[0].strip())
        except Exception:
            pass

        # 3. Alle installierten AUR-Pakete ermitteln
        try:
            res_aur = subprocess.run("yay -Qm", shell=True, capture_output=True, text=True)
            aur_packages = {line.split(" ")[0].strip() for line in res_aur.stdout.split("\n") if line.strip()}
        except Exception:
            aur_packages = set()

        # 4. Filter nach GUI-Anwendungen über die .desktop-Dateiname-Heuristik
        desktop_apps = set()
        desktop_dir = "/usr/share/applications"
        if os.path.exists(desktop_dir):
            for f in os.listdir(desktop_dir):
                if f.endswith(".desktop"):
                    base_name = f.replace(".desktop", "").lower()
                    
                    for pkg in explicit_packages:
                        if pkg in base_name or base_name in pkg:
                            desktop_apps.add(pkg)

        # Sicherheits-Fallback für bekannte Core-Apps deiner Distribution
        known_guis = ["code", "visual-studio-code-bin", "vscodium-bin", "discord", "steam", "spotify"]
        for pkg in known_guis:
            if pkg in explicit_packages:
                desktop_apps.add(pkg)

        # 5. JSON-Struktur für das Frontend aufbauen
        for pkg in desktop_apps:
            has_update = pkg in updates_available
            source_type = "aur" if pkg in aur_packages else "repo"
            status_type = "update_available" if has_update else "installed"
            
            # Statt festem Text senden wir Variablen für das Frontend
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
    server = HTTPServer(('127.0.0.1', 8080), StoreAPIHandler)
    print("The Kader⁴² App Store REST API is hosted at http://127.0.0.1:8080")
    server.serve_forever()