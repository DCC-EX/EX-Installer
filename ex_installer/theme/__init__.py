"""
Set up theme
"""

from pathlib import Path
import sys

try:
    THEME_PATH = Path(sys._MEIPASS) / "theme"
except Exception:
    if getattr(sys, "frozen", False):
        THEME_PATH = Path(sys.executable).parent / "theme"
    else:
        THEME_PATH = Path(__file__).parent

"""DCC-EX theme"""
DCC_EX_THEME = THEME_PATH / "dcc-ex-theme.json"
