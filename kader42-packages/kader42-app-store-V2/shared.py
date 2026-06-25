#!/usr/bin/usr/env python
# /usr/lib/kader-store/shared.py
import sqlite3
import os
import configparser
import pyalpm
import sys
import re


from pathlib import Path

DB_PATH = Path("~/.config/kader42/software-center.db").expanduser()
CACHE_DIR = os.path.expanduser("~/.cache/kader-store/icons/")

def init_environment():
    # Create directories if they do not exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                source TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                progress INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Enable WAL mode for concurrent read/write operations
        conn.execute("PRAGMA journal_mode=WAL;")

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