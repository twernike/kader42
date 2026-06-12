# /usr/lib/kader-store/worker.py
import sqlite3
import time
import subprocess
import pyalpm
import configparser
import os
import sys
import re
from shared import DB_PATH

def parse_mirrorlist(mirrorlist_path):
    """Extrahiert alle aktiven Server-URLs aus einer Pacman-Mirrorlist-Datei"""
    servers = []
    if not os.path.exists(mirrorlist_path):
        return servers
        
    with open(mirrorlist_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Server"):
                match = re.match(r"^Server\s*=\s*(.+)$", line)
                if match:
                    servers.append(match.group(1).strip())
    return servers

def prepare_alpm_handle():
    """Erstellt ein ALPM-Handle und konfiguriert alle Repositories inkl. Mirrorlists"""
    handle = pyalpm.Handle("/", "/var/lib/pacman")
    
    if not os.path.exists("/etc/pacman.conf"):
        return handle

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("/etc/pacman.conf")

    for section in config.sections():
        if section in ["options"]:
            continue
            
        try:
            db = handle.register_syncdb(section, pyalpm.SIG_DATABASE_OPTIONAL)
            repo_servers = []
            
            # 1. Direkt definierte Server (z.B. [kader42])
            if config.has_option(section, "Server"):
                server_val = config.get(section, "Server")
                if server_val:
                    repo_servers.append(server_val.strip())
            
            # 2. Includierte Mirrorlists (core, extra, etc.)
            if config.has_option(section, "Include"):
                include_path = config.get(section, "Include")
                if not include_path.startswith("/"):
                    include_path = os.path.join("/etc", include_path)
                    
                mirrors = parse_mirrorlist(include_path)
                for mirror in mirrors:
                    repo_servers.append(mirror.replace("$repo", section))
            
            # Zuweisung an das pyalpm C-Objekt
            db.servers = repo_servers
                    
        except Exception as e:
            print(f"Fehler beim Registrieren von [{section}]: {e}", file=sys.stderr)
            
    return handle

def execute_package_action(job):
    job_id = job['id']
    pkg_name = job['package_name']
    action = job['action']
    
    if not pkg_name.isalnum() and not any(c in pkg_name for c in ['-', '_', '+', '.']):
        raise ValueError("Ungültiger Paketname!")

    if action in ["install", "update"]:
        update_progress(job_id, "installing", 20)
        # Bleibt so: yay baut im User-Kontext, sudoloop hält es offen
        # cmd = ["/usr/bin/yay", "-Sy", "--noconfirm", "--sudoloop", pkg_name]
        cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Sy", "--noconfirm", pkg_name]

            
    elif action == "remove":
        update_progress(job_id, "removing", 20)
        # pkexec öffnet das native, wunderschöne KDE-Polkit-Passwortfenster.
        # Da drunter rufen wir direkt yay auf, das dann sofort die nötigen Rechte hat!
        cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Rns", "--noconfirm", pkg_name]
    else:
        return

    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print(f"Worker-Fehler bei {action} von {pkg_name}: {process.stderr}")
        raise Exception(f"Fehler bei {action}: {process.stderr if process.stderr else process.stdout}")

def recovery_on_startup():
    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        conn.execute("""
            UPDATE jobs 
            SET status='interrupted', progress=0, updated_at=CURRENT_TIMESTAMP 
            WHERE status='running' OR status='building' OR status='installing'
        """)
        conn.commit()

def get_next_job():
    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, package_name, source, action FROM jobs WHERE status='queued' ORDER BY id ASC LIMIT 1"
        )
        job = cursor.fetchone()
        if job:
            conn.execute(
                "UPDATE jobs SET status='running', updated_at=CURRENT_TIMESTAMP WHERE id=?", 
                (job['id'],)
            )
            conn.commit()
            return job
    return None

def update_progress(job_id, status, progress):
    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        conn.execute(
            "UPDATE jobs SET status=?, progress=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, progress, job_id)
        )
        conn.commit()

def worker_loop():
    print("Kader⁴² Store Worker daemon is active and waiting for jobs...")
    
    initialized = False
    while not initialized:
        if os.path.exists(DB_PATH):
            try:
                recovery_on_startup()
                initialized = True
            except sqlite3.OperationalError:
                time.sleep(1)
        if not initialized:
            time.sleep(1)

    print("Verbindung zur API-Datenbank erfolgreich hergestellt. Bereit für Jobs.")

    while True:
        try:
            job = get_next_job()
            if not job:
                time.sleep(1)
                continue
                
            print(f"Verarbeite Job {job['id']}: {job['action']} {job['package_name']}")
            execute_package_action(job)
            update_progress(job['id'], "completed", 100)
            print(f"Job {job['id']} erfolgreich beendet.")
            
        except sqlite3.OperationalError:
            time.sleep(0.5)
            continue
        except Exception as e:
            print(f"Fehler bei Job: {e}", file=sys.stderr)
            try:
                if 'job' in locals() and job:
                    update_progress(job['id'], "failed", 0)
            except:
                pass
            time.sleep(1)

if __name__ == "__main__":
    worker_loop()