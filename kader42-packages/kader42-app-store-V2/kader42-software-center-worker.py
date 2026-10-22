#!/usr/bin/env python
# /usr/lib/kader-store/kader42-software-center-worker.py
import sqlite3
import time
import subprocess
import os
import sys
import re
import json
from datetime import datetime, timedelta
from shared import DB_PATH, prepare_alpm_handle

handle = prepare_alpm_handle()
SETTINGS_FILE = "/etc/kader42/software-center.json"

def get_retention_settings():
    """Liest die Retention-Tage aus den Einstellungen (Defaults: Completed=1, Failed=3)."""
    completed_days = 1
    failed_days = 3
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                completed_days = int(data.get("retention_completed_days", 1))
                failed_days = int(data.get("retention_failed_days", 3))
        except Exception as e:
            print(f"[worker] Fehler beim Lesen der Retention-Settings: {e}")
    return completed_days, failed_days

def ensure_database_schema():
    """Automatisches Schema-Update: Fügt 'log_output' und 'created_at' hinzu."""
    if not os.path.exists(DB_PATH):
        return

    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "log_output" not in columns:
            print("[worker] Auto-Migration: Spalte 'log_output' wird hinzugefügt...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN log_output TEXT DEFAULT ''")
            
        if "created_at" not in columns:
            print("[worker] Auto-Migration: Spalte 'created_at' wird hinzugefügt...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            
        conn.commit()

def cleanup_old_jobs():
    """Löscht veraltete Jobs automatisch basierend auf Erstellungsdatum und Status."""
    completed_days, failed_days = get_retention_settings()
    now = datetime.now()
    
    completed_cutoff = (now - timedelta(days=completed_days)).strftime("%Y-%m-%d %H:%M:%S")
    failed_cutoff = (now - timedelta(days=failed_days)).strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        cursor = conn.cursor()
        # Lösche erfolgreiche Jobs
        cursor.execute(
            "DELETE FROM jobs WHERE status = 'completed' AND (created_at < ? OR updated_at < ?)",
            (completed_cutoff, completed_cutoff)
        )
        # Lösche fehlgeschlagene/unterbrochene Jobs
        cursor.execute(
            "DELETE FROM jobs WHERE status IN ('failed', 'interrupted') AND (created_at < ? OR updated_at < ?)",
            (failed_cutoff, failed_cutoff)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        if deleted_count > 0:
            print(f"[worker] Auto-Cleanup: {deleted_count} alte Jobs aus der Datenbank entfernt.")

def execute_package_action(job):
    job_id = job['id']
    pkg_name = job['package_name']
    action = job['action']
    
    if pkg_name == "system-update" and action == "update":
        update_progress(job_id, "installing", 20)
        
        def run_update_process(extra_flags=None, initial_log=""):
            cmd = ["/usr/bin/yay", "--sudo", "/usr/bin/pkexec", "-Syu", "--noconfirm", "--needed"]
            if extra_flags:
                cmd.extend(extra_flags)
                
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            log_acc = initial_log
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    log_acc += line
                    recent_log = log_acc[-8000:]
                    try:
                        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
                            conn.execute("UPDATE jobs SET log_output = ? WHERE id = ?", (recent_log, job_id))
                            conn.commit()
                    except Exception:
                        pass

            process.wait()
            return process.returncode, log_acc

        returncode, log_accumulator = run_update_process()
        
        if returncode != 0:
            conflict_signatures = ["existiert im Dateisystem", "exists in filesystem", "conflicting files", "Dateikonflikte"]
            if any(sig.lower() in log_accumulator.lower() for sig in conflict_signatures):
                notice = "\n\n⚠️ Datei-Konflikt erkannt! Auto-Reparatur mit '--overwrite \"*\"'...\n\n"
                returncode, log_accumulator = run_update_process(extra_flags=["--overwrite", "*"], initial_log=log_accumulator + notice)

            pgp_sigs = ["unknown public key", "unbekannter öffentlicher schlüssel", "failed (unknown public key)"]
            if any(sig in log_accumulator.lower() for sig in pgp_sigs):
                key_match = re.search(r'(?:unknown public key|unbekannter öffentlicher Schlüssel)\s+([A-F0-9]{16})', log_accumulator, re.IGNORECASE)
                if key_match:
                    missing_key = key_match.group(1)
                    notice = f"\n\n🔑 PGP-Schlüssel {missing_key} importieren...\n\n"
                    subprocess.run(["/usr/bin/gpg", "--recv-keys", missing_key], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)                        
                    returncode, log_accumulator = run_update_process(initial_log=log_accumulator + notice)

        recent_log = log_accumulator[-8000:] if log_accumulator else "Keine Konsolen-Ausgabe erfasst."
        
        if returncode != 0:
            with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
                conn.execute("UPDATE jobs SET log_output = ?, status = 'failed' WHERE id = ?", (recent_log, job_id))
                conn.commit()
            raise Exception(f"Update fehlgeschlagen mit Exit Code {returncode}")
        
    else:
        if not pkg_name.isalnum() and not any(c in pkg_name for c in ['-', '_', '+', '.']):
            raise ValueError("Ungültiger Paketname!")

        if action == "install":
            update_progress(job_id, "installing", 20)
            cmd = ["/usr/bin/yay", "--sudo", "/usr/bin/pkexec", "-S", "--noconfirm", pkg_name]
        elif action == "update":
            update_progress(job_id, "installing", 20)
            cmd = ["/usr/bin/yay", "--sudo", "/usr/bin/pkexec", "-S", "--noconfirm", pkg_name]
        elif action == "remove":
            update_progress(job_id, "removing", 20)
            cmd = ["/usr/bin/yay", "--sudo", "/usr/bin/pkexec", "-Rns", "--noconfirm", pkg_name]
        else:
            return

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        log_acc = ""
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                log_acc += line
                recent_log = log_acc[-8000:]
                try:
                    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
                        conn.execute("UPDATE jobs SET log_output = ? WHERE id = ?", (recent_log, job_id))
                        conn.commit()
                except Exception:
                    pass

        process.wait()
        if process.returncode != 0:
            raise Exception(f"Aktion fehlgeschlagen mit Exit Code {process.returncode}")

def recovery_on_startup():
    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        conn.execute("""
            UPDATE jobs 
            SET status='interrupted', progress=0, updated_at=CURRENT_TIMESTAMP 
            WHERE status IN ('running', 'building', 'installing', 'removing')
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
    print("Kader⁴² Software Center Worker Daemon gestartet...")
    
    initialized = False
    while not initialized:
        if os.path.exists(DB_PATH):
            try:
                ensure_database_schema()
                recovery_on_startup()
                cleanup_old_jobs()
                initialized = True
            except sqlite3.OperationalError:
                time.sleep(1)
        if not initialized:
            time.sleep(1)

    print("[worker] Verbingung hergestellt. Warten auf Jobs...")
    last_cleanup = time.time()

    while True:
        try:
            # Stündlicher Auto-Cleanup der Datenbank
            if time.time() - last_cleanup > 3600:
                cleanup_old_jobs()
                last_cleanup = time.time()

            job = get_next_job()
            if not job:
                time.sleep(1)
                continue
                
            print(f"[worker] Verarbeite Job {job['id']}: {job['action']} {job['package_name']}")
            execute_package_action(job)
            update_progress(job['id'], "completed", 100)
            print(f"[worker] Job {job['id']} erfolgreich abgeschlossen.")
            
        except sqlite3.OperationalError:
            time.sleep(0.5)
            continue
        except Exception as e:
            print(f"[worker] Fehler bei Job: {e}", file=sys.stderr)
            try:
                if 'job' in locals() and job:
                    update_progress(job['id'], "failed", 0)
            except:
                pass
            time.sleep(1)

if __name__ == "__main__":
    worker_loop()