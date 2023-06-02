# EX-Installer

A Python based cross-platform installer

## PyInstaller build

Windows command:

`pyinstaller --windowed --clean --onefile --icon=ex_installer\images\dccex-logo.png ex_installer.py --name "EX-Installer" --add-data "C:\Code\EX-Installer\ex_installer\images\*;images" --add-data "C:\Code\EX-Installer\ex_installer\theme\dcc-ex-theme.json;theme/." --add-data "C:\Code\EX-Installer\venv\Lib\site-packages\customtkinter;customtkinter"`
