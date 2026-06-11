import os
import sys
import shutil
from pathlib import Path

# Add root directory to path initially
root_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(root_dir))

# Check if running under Vercel
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    tmp_app_dir = Path("/tmp/app")
    if not tmp_app_dir.exists():
        print(f"[Vercel Boot] Replicating app workspace from {root_dir} to {tmp_app_dir}...")
        ignore_patterns = shutil.ignore_patterns(
            '.git', '.env', '__pycache__', 'api', 'scratch', 'node_modules'
        )
        shutil.copytree(str(root_dir), str(tmp_app_dir), ignore=ignore_patterns)
        
        # Ensure raw data and output directories exist
        (tmp_app_dir / "data" / "raw").mkdir(parents=True, exist_ok=True)
        (tmp_app_dir / "output" / "charts").mkdir(parents=True, exist_ok=True)
        print("[Vercel Boot] App workspace replication complete.")
    
    # Change current working directory to the writable /tmp/app
    os.chdir(str(tmp_app_dir))
    
    # Ensure /tmp/app is at the front of sys.path so we load files from it
    if str(tmp_app_dir) not in sys.path:
        sys.path.insert(0, str(tmp_app_dir))
    if '' in sys.path:
        sys.path.remove('')
    sys.path.insert(0, '')

# Now import the app from the current directory (which will be /tmp/app on Vercel)
from app import app
