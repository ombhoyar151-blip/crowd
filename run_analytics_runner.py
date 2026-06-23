import sys
import runpy
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

# Execute the analytics script as __main__ so it sees CLI args passed to this wrapper.
runpy.run_path(str(repo_root / "scripts" / "run_analytics.py"), run_name="__main__")
