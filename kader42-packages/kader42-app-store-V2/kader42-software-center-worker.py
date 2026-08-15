#!/usr/bin/env python
# /usr/lib/kader-store/kader42-software-center-worker.py
import sqlite3
import time
import subprocess
import os
import sys
import re
from shared import DB_PATH, prepare_alpm_handle

handle = prepare_alpm_handle()

def ensure_database_schema():
    """Automatisches Schema-Update: Fügt fehlende Spalten geräuschlos hinzu."""
    if not os.path.exists(DB_PATH):
        return

    with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
        cursor = conn.cursor()
        
        # Reads all existing columns from the ‘jobs’ table
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Checks whether ‘log_output’ is missing
        if "log_output" not in columns:
            print("[kader42-software-center-worker] Auto-Migration: The ‘log_output’ column is being added...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN log_output TEXT DEFAULT ''")
            conn.commit()
            print("[kader42-software-center-worker] Auto-migration completed successfully.")

def execute_package_action(job):
    job_id = job['id']
    pkg_name = job['package_name']
    action = job['action']
    
    #  1. Special Case: Global System Update (“Update All”)
    if pkg_name == "system-update" and action == "update":
        update_progress(job_id, "installing", 20)
        
        # Helper function for running `yay` with live logging
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
                    recent_log = log_acc[-4000:]
                    try:
                        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
                            conn.execute("UPDATE jobs SET log_output = ? WHERE id = ?", (recent_log, job_id))
                            conn.commit()
                    except Exception:
                        pass

            process.wait()
            return process.returncode, log_acc

        # 1. First regular update attempt
        returncode, log_accumulator = run_update_process()
        
        # 2. Automatic conflict detection in case of failure
        if returncode != 0:
            conflict_signatures = [
                "existiert im Dateisystem",
                "exists in filesystem",
                "conflicting files",
                "Dateikonflikte"
            ]
            
            # Check whether the failure was caused by file conflicts
            has_file_conflict = any(sig.lower() in log_accumulator.lower() for sig in conflict_signatures)
            
            if has_file_conflict:
                notice = "\n\n⚠️ File conflict detected! Start automatic repair attempt with '--overwrite' \"*\"'...\n\n"
                print("[kader42-software-center-worker] File conflict detected. Start auto-repair with --overwrite...")
                
                # Second pass with --overwrite “*”
                returncode, log_accumulator = run_update_process(
                    extra_flags=["--overwrite", "*"], 
                    initial_log=log_accumulator + notice
                )

            pgp_sigs = ["unknown public key", "unbekannter öffentlicher schlüssel", "failed (unknown public key)"]
            has_pgp_error = any(sig in log_accumulator.lower() for sig in pgp_sigs)
                
            if has_pgp_error:
                # Search for the Hex Key ID in the log stream
                key_match = re.search(r'(?:unknown public key|unbekannter öffentlicher Schlüssel)\s+([A-F0-9]{16})', log_accumulator, re.IGNORECASE)
                    
                if key_match:
                    missing_key = key_match.group(1)
                    notice = f"\n\n🔑 Fehlenden PGP-Schlüssel {missing_key} importieren...\n\n"
                    print(f"[kader42-worker] PGP-Key {missing_key} fehlt. Importiere via GPG...")
                        
                    # Retry after importing the key
                    gpg_cmd = ["/usr/bin/gpg", "--recv-keys", missing_key]
                    subprocess.run(gpg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)                        
                    returncode, log_accumulator = run_update_process(
                        initial_log=log_accumulator + notice
                    )

        recent_log = log_accumulator[-4000:] if log_accumulator else "Keine Konsolen-Ausgabe erfasst."
        
        # 3. Final Check
        if returncode != 0:
            with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
                conn.execute("UPDATE jobs SET log_output = ?, status = 'failed' WHERE id = ?", (recent_log, job_id))
                conn.commit()
            raise Exception(f"Update fehlgeschlagen mit Exit Code {returncode}")
        
    # if pkg_name == "system-update" and action == "update":
    #     update_progress(job_id, "installing", 20)
    #     cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Syu", "--noconfirm", "--needed"]

    # 2. Regular Individual Packages (Validation & Commands)
    else:
        if not pkg_name.isalnum() and not any(c in pkg_name for c in ['-', '_', '+', '.']):
            raise ValueError("[kader42-software-center-worker] Invalid package name!")

        if action == "install":
            update_progress(job_id, "installing", 20)
            cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-S", "--noconfirm", pkg_name]

        elif action == "update":
            update_progress(job_id, "installing", 20)
            cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-S", "--noconfirm", pkg_name]

        elif action == "remove":
            update_progress(job_id, "removing", 20)
            cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Rns", "--noconfirm", pkg_name]
            
        else:
            return

    # execute process
    process = subprocess.run(cmd, capture_output=True, text=True)
    

    if process.returncode != 0:
        # Filter out the curl progress output to see the actual Pacman error message: Document Type Abbreviation
        error_msg = process.stderr if process.stderr else process.stdout
        print(f"[kader42-software-center-worker] Update failed: {error_msg}")
        raise Exception(f"Update Aborted (Package Conflict or Network Error).")

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
    print("Kader⁴² Software Center Worker daemon is active and waiting for jobs...")
    
    initialized = False
    while not initialized:
        if os.path.exists(DB_PATH):
            try:
                ensure_database_schema()
                recovery_on_startup()
                initialized = True
            except sqlite3.OperationalError:
                time.sleep(1)
        if not initialized:
            time.sleep(1)

    print("[Kader42-software-center-worker] Connection to the API database established successfully. Ready for jobs.")

    while True:
        try:
            job = get_next_job()
            if not job:
                time.sleep(1)
                continue
                
            print(f"[Kader42-software-center-worker] Process Job {job['id']}: {job['action']} {job['package_name']}")
            execute_package_action(job)
            update_progress(job['id'], "completed", 100)
            print(f"Job {job['id']} completed successfully.")
            
        except sqlite3.OperationalError:
            time.sleep(0.5)
            continue
        except Exception as e:
            print(f"[Kader42-software-center-worker] Error in Job: {e}", file=sys.stderr)
            try:
                if 'job' in locals() and job:
                    update_progress(job['id'], "failed", 0)
            except:
                pass
            time.sleep(1)

if __name__ == "__main__":
    worker_loop()