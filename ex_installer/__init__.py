"""
Initialisation module

© 2023, Peter Cole.
All rights reserved.

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

import sys
import os

# In Linux we also need to set up SSL certs properly
if getattr(sys, "frozen", None):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)
    basedir = os.path.normpath(basedir)
os.environ["SSL_CERT_FILE"] = os.path.join(basedir, "certifi", "cacert.pem")
print(os.path.join(basedir, "certifi", "cacert.pem"))
for name, value in os.environ.items():
    print("{0}: {1}".format(name, value))

input("Wait here")
