"""
Python script to run as a wrapper around PyInstaller to simplify application builds

This script takes the appropriate command line arguments required to build the application
, generates the correct versioning info, and builds for the provided platform


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

# Import Python modules
import argparse
import os
import re
import PyInstaller.__main__
import sysconfig

# Import local modules
from ex_installer.version import ex_installer_version
from ex_installer.file_manager import FileManager as fm

# Create the argument parser and add the various required arguments
parser = argparse.ArgumentParser()

parser.add_argument("-P", "--platform", help="Platform type: Win32|Win64|Linux32|Linux64|macOS",
                    choices=["Win32", "Win64", "Linux32", "Linux64", "macOS"], required=True,
                    dest="platform")
parser.add_argument("-D", "--directory", help="Directory containing the cloned repository and virtual environment",
                    required=True,
                    dest="directory")

# Read arguments
args = parser.parse_args()


def is_file(file):
    """
    Check if provided path exists and is a file
    """
    if os.path.exists(file) and os.path.isfile(file):
        return True
    else:
        return False


def is_dir(dir):
    """
    Check if provided directory exists and is a directory
    """
    if os.path.exists(dir) and os.path.isdir(dir):
        return True
    else:
        return False


def write_version_file(major, minor, patch, platform):
    """
    Function to create file_version.txt used to define Windows exe details
    """
    file_contents = [
        "VSVersionInfo(\n",
        "  ffi=FixedFileInfo(\n"
        f"    filevers=({major}, {minor}, {patch}, 0),\n",
        f"    prodvers=({major}, {minor}, {patch}, 0),\n",
        "    mask=0x0,\n",
        "    flags=0x0,\n",
        "    OS=0x0,\n",
        "    fileType=0x0,\n",
        "    subtype=0x0,\n",
        "    date=(0, 0)\n",
        "  ),\n",
        "  kids=[\n",
        "    StringFileInfo(\n",
        "    [\n",
        "    StringTable(\n",
        "        '040904b0',\n",
        "        [StringStruct('CompanyName', 'DCC-EX'),\n",
        "        StringStruct('FileDescription', 'EX-Installer'),\n",
        "        StringStruct('InternalName', 'EX-Installer'),\n",
        f"        StringStruct('OriginalFilename', 'EX-Installer-{platform}'),\n",
        "        StringStruct('ProductName', 'EX-Installer'),\n",
        f"        StringStruct('ProductVersion', '{major}.{minor}.{patch}'),\n",
        f"        StringStruct('FileVersion', '{major}.{minor}.{patch}')])\n",
        "    ]),\n",
        "    VarFileInfo([VarStruct('Translation', [1033, 1200])])\n",
        "]\n",
        ")\n",
    ]
    windows_file_version = os.path.join(repo_dir, "file_version.txt")
    write_file = fm.write_config_file(windows_file_version, file_contents)
    if write_file != windows_file_version:
        print(f"Could not write file: {write_file}")
        return False
    else:
        return True


def get_site_packages_path():
    """
    Use sysconfig to obtain the site-packages path
    """
    return sysconfig.get_paths()["platlib"]


# Validate and assign variables
platform_name = args.platform

if is_dir(args.directory):
    repo_dir = args.directory
else:
    print(f"Provided directory {args.directory} is not valid")
    exit()

# Get path to app image and ensure it's valid
if is_file(os.path.join(repo_dir, "ex_installer", "images", "dccex-logo.png")):
    icon_file = os.path.join(repo_dir, "ex_installer", "images", "dccex-logo.png")
else:
    print(f"Provided directory {repo_dir} is missing the DCC-EX logo")
    exit()

# Get path to main script and ensure it's valid
if is_file(os.path.join(repo_dir, "ex_installer", "__main__.py")):
    script_file = os.path.join(repo_dir, "ex_installer", "__main__.py")
else:
    print(f"Provided directory {repo_dir} is missing the main Python script")
    exit()

# Set up other required parameters
images_dir = os.path.join(repo_dir, "ex_installer", "images", "*")
theme_file = os.path.join(repo_dir, "ex_installer", "theme", "dcc-ex-theme.json")
app_name = "EX-Installer-" + platform_name

# Make sure the version in ex_installer/version.py is valid
version_test = r"^(\d*)\.(\d*)\.(\d*)$"
test_version = re.match(version_test, ex_installer_version)
if test_version:
    major = test_version[1]
    minor = test_version[2]
    patch = test_version[3]
    app_version = test_version[0]
else:
    print(f"The version {ex_installer_version} defined in {os.path.join('ex_installer', 'version.py')} is not valid")
    exit()

# Write the version file for Windows apps
write_file = write_version_file(major, minor, patch, platform_name)
if not write_file:
    exit()

# Get the right directory to include customtkinter
customtkinter_dir = os.path.join(get_site_packages_path(), "customtkinter")

# Get the right directory to include CTkMessagebox icons
ctkmessagebox_dir = os.path.join(get_site_packages_path(), "CTkMessagebox", "icons")

# Display the version info for confirmation in case it hasn't been updated yet
confirm = input(f"This will build {app_name} version {app_version}. If the version should be updated, " +
                "please edit 'ex_installer/version.py'.\n" +
                "Press Y|y to confirm and continue.")
if confirm != "y" and confirm != "Y":
    exit()

# Define platform agnostic PyInstaller parameters
param_list = [
    "--windowed",
    "--clean",
    "--onefile",
    f"--icon={icon_file}",
    "--name",
    f"{app_name}"
]

# Append Windows specific parameters
if platform_name.startswith("Win"):
    param_list += [
        "--add-data",
        f"{images_dir};images",
        "--add-data",
        f"{theme_file};theme/.",
        "--add-data",
        f"{customtkinter_dir};customtkinter",
        "--add-data",
        f"{ctkmessagebox_dir};CTkMessagebox/icons",
        "--version-file",
        "file_version.txt"
    ]
# Append non-Windows parameters
else:
    param_list += [
        "--add-data",
        f"{images_dir}:images",
        "--add-data",
        f"{theme_file}:theme/.",
        "--add-data",
        f"{customtkinter_dir}:customtkinter",
        "--add-data",
        f"{ctkmessagebox_dir}:CTkMessagebox/icons",
        "--hidden-import=PIL._tkinter_finder"
    ]
# Append Linux specific parameters
if platform_name.startswith("Lin"):
    param_list += [
        "--additional-hooks-dir=."
    ]
param_list += [script_file]
print(param_list)

try:
    PyInstaller.__main__.run(param_list)
except Exception as error:
    print(str(error))
