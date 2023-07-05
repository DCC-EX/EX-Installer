"""
Module for the various images in use

© 2023, Peter Cole. All rights reserved.

This file is part of EX-Installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CommandStation.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import sys

try:
    IMAGE_PATH = Path(sys._MEIPASS) / "images"
except Exception:
    if getattr(sys, "frozen", False):
        IMAGE_PATH = Path(sys.executable).parent / "images"
    else:
        IMAGE_PATH = Path(__file__).parent

"""DCC-EX icons"""
DCC_EX_ICON_ICO = IMAGE_PATH / "dccex.ico"

"""Product logos"""
DCC_EX_LOGO = IMAGE_PATH / "dccex-logo.png"
EX_COMMANDSTATION_LOGO = IMAGE_PATH / "product-logo-ex-commandstation.png"
EX_DCCINSPECTOR_LOGO = IMAGE_PATH / "product-logo-ex-dccinspector.png"
EX_FASTCLOCK_LOGO = IMAGE_PATH / "product-logo-ex-fastclock.png"
EX_INSTALLER_LOGO = IMAGE_PATH / "product-logo-ex-installer.png"
EX_IOEXPANDER_LOGO = IMAGE_PATH / "product-logo-ex-ioexpander.png"
EX_TURNTABLE_LOGO = IMAGE_PATH / "product-logo-ex-turntable.png"

"""Button arrows"""
BACK_ARROW = IMAGE_PATH / "back-arrow.png"
NEXT_ARROW = IMAGE_PATH / "next-arrow.png"
