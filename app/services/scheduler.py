import os

import time
import threading
import requests
from datetime import datetime
from app.core.database import SessionLocal
from app.models.automation_job import AutomationJob
from app.models.job_run_log import JobRunLog


from datetime import datetime
...

def run_job(job: AutomationJob, db):
    status = "success"
    output = ""

    try:
        if job.job_type == "http_ping":
            response = requests.get(job.target, timeout=5)
            output = f"Status: {response.status_code}"
            if response.status_code >= 400:
                status = "failed"

        elif job.job_type == "python_script":
            import subprocess

            # SECURITY: only allow scripts inside the project /scripts folder
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            scripts_dir = os.path.join(project_root, "scripts")

            target_path = os.path.abspath(job.target)

            # Only allow paths under scripts_dir
            if not target_path.startswith(os.path.abspath(scripts_dir) + os.sep):
                raise ValueError(f"Blocked script path (must be inside {scripts_dir}): {target_path}")

            # Run the script using the current python interpreter
            result = subprocess.run(
                ["python", target_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
            if result.returncode != 0:
                status = "failed"


        else:
            status = "failed"
            output = "Unknown job type."

    except Exception as e:
        status = "failed"
        output = str(e)

    log = JobRunLog(
        job_id=job.id,
        status=status,
        output=output,
        # started_at will use DB default; finished_at/message can stay null
    )
    db.add(log)
    db.commit()



def scheduler_loop():
    """Runs forever in background."""
    while True:
        db = SessionLocal()

        jobs = db.query(AutomationJob).filter_by(is_active=True).all()

        for job in jobs:
            run_job(job, db)

        db.close()
        time.sleep(30)  # runs every 30s


def start_scheduler():
    """Start scheduler thread alongside FastAPI."""
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
