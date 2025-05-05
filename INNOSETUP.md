# Experimenting with Inno Setup

Trying an experiment to see if distributing EX-Installer as an installed application rather than a pre-compiled single .exe with PyInstaller can help alleviate the anti-virus and Windows Defender issues users are experiencing.

To be able to use Inno Setup, we need to have a way of installing not just the EX-Installer Python modules, but also a version of Python that will work on Windows systems that have no existing Python installation, but also not conflict with those that do have an existing installation.

## New Portable Python - 3.13

These experiments are being run with Python 3.13 to ensure the latest  version is in use and to take advantage of any new bug fixes and security updates.

To help with simpler distribution, WinPython 3.13.2 is being used to allow Python to be distributed without needing to be installed or managed separately, which also ensures a contained version that does not impact, and is not impacted by, other Python versions.

### Setting up WinPython

Download the WinPython zip file and copy the included "python" directory to the root of the EX-Installer directory.

### Adding EX-Installer packages to WinPython

Download  the .whl files for each required package identified in requirements-313.txt into a "downloads directory in the root of the EX-Installer directory.

Extract the contents of each .whl file using WinPython:

```
python\python.exe -m zipfile -e downloads\<.whl file> python\Lib
```

You will need to force reinstall Pillow to fix the missing "_imaging" binary:

```
python\python.exe -m pip install --force-reinstall --no-cache-dir Pillow
```

This may also work with WinPython's pip module:

```
python\python.exe -m pip install -r requirements-313.txt
```

### Test EX-Installer

At this point, EX-Installer should run as a module with:

```
python\python.exe -m ex_installer
```

## Initial Test

Mounting the EX-Installer directory on my local machine to an Oracle VirtualBox Windows VM with no version of Python or anything else installed via a shared folder enabled me to run EX-Installer using the WinPython version of Python and was able to successfully download the Arduino CLI and compile for a fake device.

## Inno Setup

Install Inno Setup 6 (6.4.3 at time of writing), and note there is a VSCode Extension "Inno Setup" that will help with syntax etc.
