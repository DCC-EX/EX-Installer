# EX-Installer

EX-Installer is a Python based, cross-platform installer for the various Arduino based DCC-EX products.

Binaries will be made available to allow EX-Installer to be run on:

- Windows 10/11
- Linux graphical environments
- macOS

It is possible that it will also be able to run on Raspberry Pi.

## What's in this repository?

This repository includes all source code of EX-Installer, along with related documentation and screen captures of the initial design ideas.

The binaries are kept in the /dist directory of the repository, and will also be hosted on the [DCC-EX website](https://dcc-ex.com).

## Operating principles and modules

EX-Installer operates within the confines of the user's home directory and temp directory only, with no files or folders outside of these directories being touched.

In Windows, this will typically be `C:\Users\<username>\ex-installer`, and in Linux or macOS `/home/<username>/ex-installer`.

The general operating process of the installer is:

- Download/extract the Arduino CLI
- Detect attached Arduino devices
- Clone the product's GitHub repository
- Prompt for version selection and configuration options
- Compile and upload the configured software to the selected device

The main Python modules in use are:

- [CustomTkinter](https://customtkinter.tomschimansky.com/) to create a reasonably modern look and feel
- [CTkMessagebox](https://github.com/Akascape/CTkMessagebox) for nicer dialogues and popups
- [pygit2](https://www.pygit2.org/index.html) to perform GitHub repository activities
- [PyInstaller](https://pyinstaller.org/en/stable/index.html) to create binaries

## Supported products

Initially, EX-Installer will be focused on basic configuration and installation of EX-CommandStation only in order to be able to replace the previous version of EX-Installer.

Once stable, it will be expanded to be able to configure and install all of our Arduino based products including:

- EX-CommandStation
- EX-DCCInspector
- EX-FastClock
- EX-IOExpander
- EX-Turntable

## Running EX-Installer

To run EX-Installer, simply download the appropriate executable or binary file for the Operating System in use.

If downloading directly from GitHub, use the "raw" file download.

Alternatively, if desired, it can be run using a local Python install as a Python module.

In this instance, it is recommended to run in a virtual environment. Assuming Python 3.x is installed:

- Clone the repository with `git clone https://github.com/DCC-EX/EX-Installer.git`
- Change into the newly created directory
- Create a virtual environment with `virtualenv venv`
- Activate the virtual environment:
  - Windows: `venv\scripts\activate`
  - Linux/macOS: `source venv/bin/activate`
- Install required modules with `pip install -r requirements.txt`
- Run as a module with `python -m ex_installer`

## How to build binaries

PyInstaller is used to build Windows executables and binaries for Linux/macOS.

The use of CustomTkinter dictates that some extra options need to be defined to ensure non-Python files are included in the binary, otherwise they will not execute correctly.

It is recommended to use a Python virtual environment to build the binaries to ensure only the relevant Python modules are included.

These directories are referenced in the commands below:

- \<repository\> - This is the directory containing the locally cloned EX-Installer repository
- \<python version\> - This is the directory containing the Python version's local packages
- \<platform\> - This is the platform the binary is built for:
  - Win64 - Windows 64 bit
  - Win32 - Windows 32 bit
  - Linux64 - Linux 64 bit
  - Linux32 - Linux 32 bit
  - macOS - macOS (64 bit only)

The build commands should be executed in a command prompt or terminal window in the directory containing the cloned repository.

Windows command:

`pyinstaller --windowed --clean --onefile --icon=ex_installer\images\dccex-logo.png ex_installer\__main__.py --name "EX-Installer-<platform>" --add-data "<repository>\ex_installer\images\*;images" --add-data "<repository>\ex_installer\theme\dcc-ex-theme.json;theme/." --add-data "<repository>\venv\Lib\site-packages\customtkinter;customtkinter"`

Linux command:

`pyinstaller --windowed --clean --onefile --icon=ex_installer/images/dccex-logo.png ex_installer/__main__.py --name "EX-Installer-<platform>" --add-data "<repository>/ex_installer/images/*:images" --add-data "<repository>/ex_installer/theme/dcc-ex-theme.json:theme/." --add-data "<repository>/venv/lib/python3.8/site-packages/customtkinter:customtkinter" --hidden-import="PIL._tkinter_finder"`
