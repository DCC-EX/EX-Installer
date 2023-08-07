"""
Version file for the application

Ensure the variable version contains a semantic versioned string

This file is read by the application at runtime if run as a module, and is also
read by the application build process to embed in the application details
"""

ex_installer_version = "0.0.15"

"""
Version history:

0.0.15      - Update config directory browse to shows files as well as folders
            - Validate user is not using EX-Installer generated config files
            - Add background update to Device Monitor to resolve bug on older Linux flavours
            - Ensure consistency of upload vs. load
            - Remove TrackManager OFF/NONE option
0.0.14      - Add timeout for Arduino CLI threads, default 5 minutes
            - Split compile/upload process out to show output of each phase
            - Add support for EX-Turntable
            - Improve error detection/handling for Arduino CLI commands
            - Fix bug where closing app with device monitor open waits for thread join and errors
            - Set device manager output to read only
            - Add option to backup generated config files to a selected folder
            - Add highlights to device monitor for version and WiFi info
            - Updated 4 row LCD definition for 20 columns
            - Add option to power on/join at startup
            - Revised EX-CommandStation configuration layout
            - Updated optional config file list for EX-CommandStation to include my*.cpp
            - Enable overriding current limit as introduced in 4.2.61
            - Enable setting WiFi hostname in ST mode
            - Enable setting loco/cab IDs in DC/DCX mode for TrackManager
0.0.13      - Add EX-IOExpander support
            - Add WiFi password validation in EX-CommandStation configuration
            - Add command history to device monitor
            - Add hover style tooltips for contextual help
            - Add info menu with about information, website link, and instructions link
0.0.12      - Enable device monitor title bar
            - Fix bug in Linux where device monitor is always on top of all windows
            - Fix bug where track manager options displaying for incorrect versions
0.0.11      - Fix build process for macOS and Linux
            - Update dealing with unsuppported operating systems in a nicer manner so
              exceptions aren't raised, but errors are handled normally
            - Update initial view switch to happen after scaling to fix Linux bug (Harald Barth)
0.0.10      - Automatically scan for devices on the Select Device view when starting
            - Enable browsing for and using existing configuration files
            - Add tabbed view for editing more than two configuration files
0.0.9       - Display serial device details for unknown/clone devices
0.0.8       - Fix for DPI scaling bug when moving monitors (Harald Barth)
0.0.7       - Add the ability to direct edit config files
            - Add track manager configuration to EX-CommandStation config
            - Disable selecting the WiFi channel in station mode for EX-CommandStation
            - Update no device found message
            - Enable/disable track manager configuration based on version
0.0.6       - Add a serial monitor for viewing serial output and sending commands
0.0.5       - Provide extra welcome information and instructions
            - Rephrase from "upload" to "load" which is potentially less confusing and more appropriate language
            - Refine Manage Arduino CLI text
            - Fix bug where navigating from Load screen crashes application due to missing version parameter
0.0.4       - Expose selected product version to product configuration view
            - Add application and product versions to generated config file
0.0.3       - Allow setting custom password for WiFi in AP mode
0.0.2       - Separate repository and version management from EX-CommandStation configuration
0.0.1       - Initial release:
            - Configure, compile, upload EX-CommandStation
            - Supports AVR, ESP32, and STM32
"""
