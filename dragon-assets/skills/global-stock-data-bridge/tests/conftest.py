"""conftest.py · 让 pytest 能找到父目录的 em_global_get.py / em_global.py"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
