"""
Module for the various images in use
"""

from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    IMAGE_PATH = Path(sys.executable).parent / "images"
else:
    IMAGE_PATH = Path(__file__).parent

"""DCC-EX icons"""
DCC_EX_ICON_ICO = IMAGE_PATH / "dccex.ico"

"""Product logos"""
DCC_EX_LOGO = IMAGE_PATH / "dccex-logo.png"
EX_COMMANDSTATION_LOGO = IMAGE_PATH / "ex-commandstation.png"
EX_DCCINSPECTOR_LOGO = IMAGE_PATH / "ex-dccinspector.png"
EX_FASTCLOCK_LOGO = IMAGE_PATH / "ex-fastclock.png"
EX_INSTALLER_LOGO = IMAGE_PATH / "ex-installer.png"
EX_IOEXPANDER_LOGO = IMAGE_PATH / "ex-ioexpander.png"
EX_TURNTABLE_LOGO = IMAGE_PATH / "ex-turntable.png"
