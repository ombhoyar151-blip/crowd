import sys
import runpy
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

runpy.run_path(str(repo_root / "scripts" / "seed_db.py"), run_name="__main__")
