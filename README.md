# EX-Installer

EX-Installer is a Python based, cross-platform installer for the various Arduino based DCC-EX products.

Binaries will be made available to allow EX-Installer to be run on:

- Windows 10/11 (64 bit only)
- Linux graphical environments (64 bit only, not Raspberry Pi)
- macOS

## What's in this repository?

This repository includes all source code of EX-Installer, along with related documentation and screen captures of the initial design ideas.

The binaries are attached to each version's release of EX-Installer, and will also be linked from the [DCC-EX website](https://dcc-ex.com).

<!-- ### EX-Installer-Configs repository

In addition to this EX-Installer repository, there is a separate repository [EX-Installer-Configs](https://github.com/DCC-EX/EX-Installer-Configs) which contains various configuration information that EX-Installer relies on.

This enables product and device configuration information to be updated without necessarily needing to build a new release of EX-Installer binaries. -->

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

Currently, EX-Installer configures and installs:

- EX-CommandStation
- EX-IOExpander
- EX-Turntable

## Running EX-Installer

To run EX-Installer on macOS or Linux, simply download the appropriate executable or binary file for the Operating System in use from the release.

On Windows, download the installation setup file "EX-Installer-Setup-Win64.exe" to install EX-Installer.

### Run as a Python module

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

## Versioning

Initially, the application is versioned by updating the file "version.py" located within the "ex_installer" module directory.

Semantic versioning is in use, with the standard `<Major>.<Minor>.<Patch>` version scheme.

The version file is reference by both the application itself as well as the binary build script outlined below.

Once all binaries for a specific version have been built and published, a GitHub tag must be created against that commit also.

## How to build binaries

**NOTE** that for Windows users, InnoSetup is now used to distribute a setup file instead, refer to `InnoSetup\INNOSETUP.md` for details on how this works.

PyInstaller is used to build binaries for Linux/macOS.

The use of CustomTkinter dictates that some extra options need to be defined to ensure non-Python files are included in the binary, otherwise they will not execute correctly.

**NOTE** when building on Linux, you must use a flavour of Linux with fontconfig version 2.13.1 or later, otherwise users of newer Linux flavours will receive warnings or exceptions relating to the "description" element in the configuration.

### Build script

A build script "build_app.py" has been written to make the build process simpler, and relies on a virtual environment being setup in a directory called "venv" within the EX-Installer repository directory.

The script will refer to the "version.py" file mentioned above, so this needs to be updated prior to building the final version of the binaries to be published.

To run the script, you need to pass the EX-Installer repository directory and the platform being built for:

```shell
python -m build_app -D <Directory path> -P <Linux64|macOS>
```

### Building manually

It is recommended to use a Python virtual environment to build the binaries to ensure only the relevant Python modules are included.

These directories are referenced in the commands below:

- \<repository\> - This is the directory containing the locally cloned EX-Installer repository
- \<python version\> - This is the directory containing the Python version's local packages
- \<platform\> - This is the platform the binary is built for:
  - Linux64 - Linux 64 bit
  - macOS - macOS (64 bit only)

The build commands should be executed in a command prompt or terminal window in the directory containing the cloned repository.

Linux/macOS command:

`pyinstaller --windowed --clean --onefile --icon=ex_installer/images/dccex-logo.png ex_installer/__main__.py --name "EX-Installer-<platform>" --add-data "<repository>/ex_installer/images/*:images" --add-data "<repository>/ex_installer/theme/dcc-ex-theme.json:theme/." --add-data "<repository>/venv/lib/python3.8/site-packages/customtkinter:customtkinter" --hidden-import="PIL._tkinter_finder"`

## EX-Installer Release Manager

To simplify the release process and ensure releases are consistent, use the provided script "ex_installer_release.py".

This script automates the release management process for EX-Installer and takes care of:

- Creating the required GitHub tag
- Creating the required GitHub release
- Uploading the required distribution files to the release
- Publishing the release

Each release will be versioned consistently based on the version defined in "ex_installer/version.py":

- Releases 0.y.z will automatically be marked "Devel"
- Releases 1.y.z or later, where y is an even number will be marked "Prod"
- Releases 1.y.z or later, where y is an odd number will be marked "Devel"

Examples:

- 0.0.21 will become "v0.0.21-Devel"
- 1.0.0 will become "v1.0.0-Prod"
- 1.1.0 will become "v1.1.0-Devel"

### Running the script

To run this script, you must copy the provided '.env.example' file to '.env' and update it.

It must contain a valid GitHub personal access token with these privileges on the DCC-EX/EX-Installer repository:

- Contents - read/write
- Deployments - read/write
- Metadata - read

When running this script, you must specify at least one of:

- -F|--files: A comma separated list of files to upload, which must be located in your local EX-Installer/dist folder
- -D|--delete: A file to be deleted from the release
- -P|--publish: If specified, the release will be published, otherwise it will be created as a draft

Note: You cannot specify both -F|--files and -D|--delete at the same time.

To publish an EX-Installer release, three distribution files are expected to be attached as assets:

- EX-Installer-Linux64 - 64bit Linux binary
- EX-Installer-macOS - macOS binary
- EX-Installer-Setup-Win64.exe - Windows 64bit installer executable built by Inno Setup

When publishing, if any of these are not present, a warning will be generated, with a prompt to continue or cancel.
