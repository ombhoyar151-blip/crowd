#!/usr/bin/env python3
"""
Quick-start helper: sets up DB, seeds data, and prints the launch commands.
Run this AFTER docker compose up postgres redis -d
"""
import subprocess, sys, os, time

DOCKER = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"

def run(cmd, cwd=None):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("=" * 60)
    print(" CrowdSense AI — Quick Start")
    print("=" * 60)

    # 1. Run migrations
    print("\n[1/3] Running Alembic migrations...")
    rc = run("alembic upgrade head")
    if rc != 0:
        print("ERROR: Migrations failed. Is PostgreSQL running?")
        sys.exit(1)
    print("✅ Migrations applied.")

    # 2. Seed DB
    print("\n[2/3] Seeding database...")
    rc = run("python scripts/seed_db.py")
    if rc != 0:
        print("WARNING: Seed may have failed (OK if already seeded).")
    else:
        print("✅ Database seeded.")

    # 3. Print instructions
    print("\n[3/3] Ready! Launch these in separate terminals:\n")
    print("  Terminal 1 (Backend):")
    print("    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("  Terminal 2 (Celery Worker):")
    print("    celery -A backend.worker.celery_app worker --loglevel=info -P solo")
    print()
    print("  Terminal 3 (Frontend):")
    print("    cd frontend && npm run dev")
    print()
    print("  Terminal 4 (Vision Pipeline):")
    print("    python scripts/run_analytics.py --video scripts/sample.mp4 --loop")
    print()
    print("=" * 60)
    print("  Dashboard: http://localhost:5173")
    print("  API Docs:  http://localhost:8000/docs")
    print("  Login:     admin / changeme")
    print("=" * 60)

if __name__ == "__main__":
    main()
