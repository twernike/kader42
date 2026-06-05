# /usr/lib/kader-store/api.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import sqlite3
import os
from shared import DB_PATH, CACHE_DIR, init_environment

class StoreAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        
        # 1. ENDPOINT: Search for apps (?search=name)
        if url_parts.path == "/apps" and "search" in query_params:
            search_term = query_params["search"][0]
            results = self.search_and_map(search_term)
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))
            
        # 2. STEP: Check the status of a job (?job_id=1)
        elif url_parts.path == "/job" and "job_id" in query_params:
            job_id = query_params["job_id"][0]
            job_status = self.get_job_status(job_id)
            self._set_headers(200)
            self.wfile.write(json.dumps(job_status).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        # 3. FINAL STEP: Create a new job (Install/Remove)
        if self.path == "/job":
            content_length = int(self.headers['Content-Length'])
            # Here, we read the body directly from rfile
            body = self.rfile.read(content_length).decode('utf-8')
            post_data = json.loads(body)
            
            pkg_name = post_data.get("package_name")
            source = post_data.get("source", "repo") # repo oder aur
            action = post_data.get("action") # install oder remove
            
            if not pkg_name or not action:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing parameters"}).encode('utf-8'))
                return
                
            # Here, we read the body directly from rfile
            job_id = self.queue_job(pkg_name, source, action)
            
            # IMPORTANT: Set the header first, then write the response
            self._set_headers(201)
            response_data = {"job_id": job_id, "status": "queued"}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def read_body(self, length):
        return self.rfile.read(length).decode('utf-8')

    def search_and_map(self, term):
        # Fallback data structure
        app_data = {
            "package_name": term,
            "source": "repo",
            "icon_path": "/usr/share/pixmaps/nobody.png", # Dein System-Fallback
            "description": "Keine Beschreibung verfügbar."
        }
        
        # Request icon and metadata from the Flathub API
        try:
            enc_term = urllib.parse.quote(term)
            flathub_url = f"https://flathub.org/api/v2/search?query={enc_term}"
            req = urllib.request.Request(flathub_url, headers={'User-Agent': 'KaderStore/1.0'})
            
            with urllib.request.urlopen(req, timeout=3) as response:
                flat_data = json.loads(response.read().decode('utf-8'))
                if flat_data:
                    best_match = flat_data[0] # Ersten Treffer nehmen
                    icon_url = best_match.get("iconUrl")
                    app_id = best_match.get("id")
                    
                    if icon_url:
                        # Cache icon locally
                        local_icon = os.path.join(CACHE_DIR, f"{app_id}.png")
                        if not os.path.exists(local_icon):
                            urllib.request.urlretrieve(icon_url, local_icon)
                        app_data["icon_path"] = local_icon
                    
                    app_data["description"] = best_match.get("summary", app_data["description"])
        except Exception:
            pass # If Flathub is offline, we use the fallbacks
            
        return [app_data]

    def queue_job(self, pkg_name, source, action):
        # timeout=20 erlaubt es der API, auf den Worker zu warten, falls dieser gerade schreibt
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO jobs (package_name, source, action) VALUES (?, ?, ?)",
                (pkg_name, source, action)
            )
            conn.commit() # Schreibt den Job sofort sicher fest
            return cursor.lastrowid

    def get_job_status(self, job_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT status, progress FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if row:
                return {"status": row["status"], "progress": row["progress"]}
            return {"status": "unknown", "progress": 0}

if __name__ == "__main__":
    init_environment()
    server = HTTPServer(('127.0.0.1', 8080), StoreAPIHandler)
    print("The Kader⁴² App Store REST API is hosted at http://127.0.0.1:8080")
    server.serve_forever()