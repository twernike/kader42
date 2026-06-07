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
        
        # 1. ENDPOINT: Kategorien abrufen
        if url_parts.path == "/categories":
            self._set_headers(200)
            self.wfile.write(json.dumps(CATEGORY_DEFINITIONS).encode('utf-8'))

        # 2. ENDPOINT: Apps einer Kategorie ODER freie Suche
        elif url_parts.path == "/apps":
            search_term = ""
            # WICHTIG: Hier prüfen wir, ob die Kategorie angefragt wurde
            if "category" in query_params:
                cat_id = query_params["category"][0]
                # Suche die passende Kategorie-Definition
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
                # Falls nichts gefunden wurde, leeres Array statt 400er Fehler, 
                # damit das UI nicht abstürzt
                self._set_headers(200)
                self.wfile.write(json.dumps([]).encode('utf-8'))
        # 4. ENDPOINT: Installierte Apps & Updates abrufen (In do_GET einbauen)
        elif url_parts.path == "/installed":
            results = self.get_installed_apps_and_updates()
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))

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
            self.wfile.write(json.dumps({"job_id": job_id, "status": "queued"}).encode('utf-8'))

    def search_via_yay(self, query):
        apps_found = []
        is_category = " " in query
        
        # ==========================================================
        # BLITZSCHNELLE KATEGORIE-ERKENNUNG (MILLISEKUNDEN-TAKT)
        # ==========================================================
        if is_category:
            terms = [t.strip() for t in query.split(" ") if t.strip()]
            
            # Einmaliger Check, welche der gängigen VS Code Varianten auf dem Framework installiert ist
            aliases = ["code", "visual-studio-code-bin", "vscodium-bin"]
            installed_vs_code = None
            for x in aliases:
                if os.path.exists(f"/var/lib/pacman/local") and any(d.startswith(f"{x}-") for d in os.listdir("/var/lib/pacman/local")):
                    installed_vs_code = x
                    break

            for term in terms:
                # Wir ermitteln den Status, indem wir direkt im lokalen Pacman-Verzeichnis nachsehen
                # Das ist unendlich viel schneller als ein subprocess-Aufruf!
                is_installed = False
                if os.path.exists("/var/lib/pacman/local"):
                    # Schaut nach, ob ein Ordner mit dem Paketnamen im lokalen Repo existiert
                    is_installed = any(d.startswith(f"{term}-") for d in os.listdir("/var/lib/pacman/local"))
                
                source_type = "repo"
                pkg_name = term
                status_type = "installed" if is_installed else "available"

                # Spezifischer VS-Code Matcher
                if term == "code" and installed_vs_code:
                    pkg_name = installed_vs_code
                    status_type = "installed"
                    if installed_vs_code == "visual-studio-code-bin":
                        source_type = "aur"
                elif term == "visual-studio-code-bin" and installed_vs_code == "visual-studio-code-bin":
                    status_type = "installed"
                    source_type = "aur"

                # Schöne, saubere Standardbeschreibungen für die Core-Apps deiner Distribution
                descriptions = {
                    "code": "Offizieller Open-Source Build von Visual Studio Code.",
                    "visual-studio-code-bin": "Microsoft Visual Studio Code (Binärversion aus dem AUR).",
                    "vscodium-bin": "Telemetriefreier Community-Build von VS Code.",
                    "firefox": "Sicherer und flexibler Open-Source Webbrowser.",
                    "chromium": "Die Open-Source Basis hinter Google Chrome.",
                    "gimp": "Professionelles Programm zur Bildbearbeitung und Manipulation.",
                    "vlc": "Universeller Medienabspieler für nahezu alle Formate.",
                    "libreoffice-fresh": "Umfangreiche und freie Office-Suite (Aktuellster Zweig).",
                    "openboard": "Interaktive Whiteboard-Software für den Bildungsbereich."
                }
                desc = descriptions.get(pkg_name, f"System-Paket aus Kader⁴² ({source_type.upper()}).")

                apps_found.append({
                    "name": pkg_name.replace("-bin", "").capitalize(),
                    "package_name": pkg_name,
                    "description": desc,
                    "source": source_type,
                    "status": status_type,
                    "icon_path": "/usr/share/pixmaps/nobody.png"
                })
            return apps_found

        # ==========================================================
        # NORMALE LIVE-SUCHE (Bleibt bei yay für freie Suchen im Suchfeld)
        # ==========================================================
        cmd = ["yay", "-Ss", "--noconfirm", query]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            lines = res.stdout.split("\n")
        except Exception:
            return apps_found

        # (Hier läuft deine bestehende yay-Suchschleife für das freie Suchfeld weiter...)
        # ... ab hier unverändert wie vorher ...
        for i in range(0, len(lines) - 1, 2):
            if not lines[i].strip(): continue
            meta = lines[i].split("/")
            if len(meta) < 2: continue
            repo_source = meta[0].strip()
            pkg_name = meta[1].split(" ")[0].strip()
            desc = lines[i+1].strip() if i+1 < len(lines) else ""
            source_type = "aur" if repo_source.lower() == "aur" else "repo"
            status_type = "installed" if "(installiert" in lines[i].lower() or "[installed" in lines[i].lower() else "available"

            apps_found.append({
                "name": pkg_name.capitalize(),
                "package_name": pkg_name,
                "description": desc,
                "source": source_type,
                "status": status_type,
                "icon_path": "/usr/share/pixmaps/nobody.png"
            })
            if len(apps_found) >= 15: break

        return apps_found
    
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
                "description": desc_key, # Hier wandert jetzt der Key rein!
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