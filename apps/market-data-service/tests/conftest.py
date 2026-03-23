import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVICE_ROOT = Path(__file__).resolve().parents[1]

for path in (ROOT, SERVICE_ROOT):
    sys.path.insert(0, str(path))
