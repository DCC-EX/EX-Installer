# Building and Distributing Windows Versions with Inno Setup

As of version 0.0.21, EX-Installer will no long be distributed as a single .exe built with PyInstaller due to the myriad of issues encountered with anti-virus applications and Windows Defender.

Instead, [Inno Setup](https://jrsoftware.org/isinfo.php) is used to build an installer, which users can use to install EX-Installer.

Given this will no longer provide a standalone, independent version of Python, [WinPython](https://winpython.github.io/) is included in the installer built with Inno Setup. This mitigates users having to install Python when they don't know how, and also prevents conflicts with other existing versions.

## Building the Windows Installer

### WinPython

Download the WinPython zip file and copy the included "python" directory to the root of the EX-Installer directory. WinPython releases are [here](https://winpython.github.io/).

Use the latest stable 64bit zip file eg. "Winpython64-3.13.0dot.zip".

The copied "python" directory should be at the same level in the directory structure as "dist", "docs", "ex_installer", and "InnoSetup".

### Install WinPython Requirements

Ensure the required Python packages are installed:

```
python\python.exe -m pip install -r InnoSetup\winpython-requirements.txt
```

Be careful to run this using the WinPython's python.exe, not any other installed version.

### Test EX-Installer

At this point, EX-Installer should run as a module with WinPython using:

```
python\python.exe -m ex_installer
```

### Inno Setup

Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php) (6.4.3 at time of writing), and note there is a VSCode Extension "Inno Setup" that will help with syntax etc.

Open Inno Setup and open the file "InnoSetup\ex-installer.iss".

To compile the installer, simply click the "Compile" button. Provided there are no errors, "EX-Installer-Setup-Win64.exe" will be compiled and located in the "dist" folder, ready to be added to the release.
