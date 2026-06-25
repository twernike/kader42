#!/usr/bin/usr/env python
# /usr/lib/kader-store/kader42-software-center-worker.py
import sqlite3
import time
import subprocess
import os
import sys
import re
from shared import DB_PATH, prepare_alpm_handle

handle = prepare_alpm_handle()


def execute_package_action(job):
    job_id = job['id']
    pkg_name = job['package_name']
    action = job['action']
    
    if not pkg_name.isalnum() and not any(c in pkg_name for c in ['-', '_', '+', '.']):
        raise ValueError("[kader42-software-center-worker] Invalid package name!")

    if action in ["install", "update"]:
        update_progress(job_id, "installing", 20)
        cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Sy", "--noconfirm", pkg_name]

            
    elif action == "remove":
        update_progress(job_id, "removing", 20)
        # pkexec opens the native, beautiful KDE Polkit password dialog.
        # Below that, we call `yay` directly, which then immediately has the necessary permissions!
        cmd = ["/usr/bin/pkexec", "/usr/bin/yay", "-Rns", "--noconfirm", pkg_name]
    else:
        return

    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print(f"Worker error during {action} in {pkg_name}: {process.stderr}")
        raise Exception(f"Error during {action}: {process.stderr if process.stderr else process.stdout}")

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