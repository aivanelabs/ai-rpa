from __future__ import annotations

import sys
from pathlib import Path


CLIENTS_PYTHON_DIR = Path(__file__).resolve().parents[1]
CLIENTS_PYTHON_SRC_DIR = CLIENTS_PYTHON_DIR / "src"

if str(CLIENTS_PYTHON_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENTS_PYTHON_SRC_DIR))
