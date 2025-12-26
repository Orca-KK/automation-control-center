# Automation Control Center (FastAPI)

A simple web-based **Automation Jobs** dashboard built with **FastAPI + Jinja2 + SQLite**.
It lets you:

- Create jobs (HTTP ping or Python script jobs)
- View existing jobs
- Run a job manually (Run button)
- Delete jobs
- View job run logs

---

## Features

### Job Types
- **http_ping**: sends an HTTP GET request to a URL and logs the status code
- **python_script**: executes a Python script **only inside the project `scripts/` folder** (basic safety guard)

### UI Pages
- `/jobs/ui` – create + manage jobs (Run/Delete)
- `/jobs/logs/ui` – view recent run logs

---

## Project Structure (typical)

