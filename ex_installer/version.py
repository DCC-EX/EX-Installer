"""
Version file for the application

Ensure the variable version contains a semantic versioned string

This file is read by the application at runtime if run as a module, and is also
read by the application build process to embed in the application details
"""

ex_installer_version = "0.0.19"

"""
Version history:

0.0.19      - Version updates, requests==2.32.2, aiohttp==3.9.4, idna==3.7, Pillow==10.3.0
            - Adjust Arduino platform installation process
            - Enforce specific versions of CLI (0.35.3), AVR (1.8.6), ESP32 (2.0.17), and STM32 (2.7.1)
            - Enforce specific version of Ethernet (2.0.2)
            - Enable fake Arduino to be selected for demo purposes using -F|--fake command line argument
            - Fix debug command line argument to update menu selection
            - Ensure the details pane on the Load screen auto scrolls to the bottom
            - Optimise myAutomation.h for Track Manager and/or auto track power on to use single sequence
            - Add user preferences file to store user settings, starting with screen scaling only
            - Update EX-CommandStation defaults for ESP32 to force enable WiFi and prevent disabling
            - Add 132 x 64 OLED
            - Add support for new DCC-EX EX-CSB1 - restricts motor driver selection
            - Fix bug where a blank myAutomation.h file cannot be disabled after being enabled
            - Add ability to install the very latest devel branch by selecting v9.9.9-Devel
            - Refactor the manage_cli() method of the manage_arduino_cli module to make it more maintainable
            - Updates to work with Arduino CLI 1.0.x as the board list output has changed
            - Revise platform and library management logic to ensure required versions only are installed
0.0.18      - Update EX-Turntable configuration options to suit changes in 0.7.0
            - Dependabot update for cryptography to 42.0.4
            - Add link to DCC-EX News articles about EX-Installer to the Info menu
            - Ensure the config backup popup is always launched within the app window geometry
            - Add a save log button to device monitor to save the device logs to a text file
            - Fix bug where copying existing config files for EX-Turntable and EX-IOExpander causes an exception
0.0.17      - Move fonts to a separate common class
            - Change default font to Arial for Windows/Mac and FreeSans for Linux
            - Update various modules versions to resolve Dependapot identified vulnerabilities
            - Remove option to select Nano with the old bootloader as this has never worked
            - Disable enabling WiFi on Uno/Nano
            - Change default behaviour of programming on Uno/Nano to enabled
            - Change start with power on option from JOIN to POWERON
            - Add warning screen to flag local repo changes and allow overriding if desired
            - Automatically discard macOS .DS_Store file if it exists
            - Allow blank WiFi password in STA mode
0.0.16      - Implement less restrictive matching for context highlights in Device Monitor
            - Implement device specific restrictions and recommendations:
            - Uno/Nano disable TrackManager, select disable EEPROM/PROG options by default
            - STM32/ESP32 select disable EEPROM option and disable switch
            - Add fix for incorrect scaling on Linux due to incorrect DPI value - Harald Barth
            - Add scaling options to menu for user selection
            - Add fix for missing Ethernet library
            - Add fix for SSL certificates missing in Fedora
0.0.15      - Update config directory browse to shows files as well as folders
            - Validate user is not using EX-Installer generated config files
            - Add background update to Device Monitor to resolve bug on older Linux flavours
            - Ensure consistency of upload vs. load
            - Remove TrackManager OFF/NONE option
            - Fix bug where TrackManager and current override options disabled for EX-CommandStation v5
            - Only generate myAutomation.h if appropriate options chosen, or switch to do so enabled
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
