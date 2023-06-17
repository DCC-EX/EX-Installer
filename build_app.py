"""
Python script to run as a wrapper around PyInstaller to simplify application builds

This script takes the appropriate command line arguments required to build the application
, generates the correct versioning info, and builds for the provided platform
"""

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-I", "--icon", help="Path to the application icon",
                    default="ex_installer/images/dccex-logo.png",
                    dest="icon")
parser.add_argument("-S", "--script", help="Path to the main script",
                    default="ex_installer/__main__.py",
                    dest="script")
parser.add_argument("-P", "--platform", help="Platform type: Win32|Win64|Linux32|Linux64|macOS",
                    choices=["Win32", "Win64", "Linux32", "Linux64", "macOS"], required=True,
                    dest="platform")
parser.add_argument("-D", "--directory", help="Directory containing the cloned repository and virtual environment",
                    required=True,
                    dest="directory")
parser.add_argument("-V", "--version", help="Version of the application being built, must be semantic versioning",
                    required=True,
                    dest="version")

# Read arguments
args = parser.parse_args()

icon_file = args.icon
script_file = args.script
platform_name = args.platform
repo_dir = args.directory
version = args.version

images_dir = os.path.join(repo_dir, "ex_installer/images/*")
theme_dir = os.path.join(repo_dir, "ex_installer/theme/dcc-ex-theme.json")
app_name = "EX-Installer" + platform_name

if platform_name.startswith("Win"):
    customtkinter_dir = os.path.join(repo_dir, "venv/Lib/site-packages/customtkinter")
else:
    customtkinter_dir = os.path.join(repo_dir, "venv/lib/python3.8/site-packages/customtkinter")

print(f"pyinstaller --windowed --clean --onefile --icon={icon_file} --name {app_name} --add-data " +
      f"{images_dir}:images")




"""
VSVersionInfo() file example included for reference:

# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(0, 0, 1, 1),
    prodvers=(0, 0, 1, 1),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x0,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x0,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x0,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904b0',
        [StringStruct('CompanyName', 'DCC-EX'),
        StringStruct('FileDescription', 'EX-Installer'),
        StringStruct('InternalName', 'EX-Installer'),
        StringStruct('OriginalFilename', 'EX-Installer'),
        StringStruct('ProductName', 'EX-Installer'),
        StringStruct('ProductVersion', '0.0.1'),
        StringStruct('FileVersion', '0.0.1')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""