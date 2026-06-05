# /usr/lib/kader-store/shared.py
import sqlite3
import os

DB_PATH = "~/.kader-store/queue.db"
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