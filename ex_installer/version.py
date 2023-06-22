"""
Version file for the application

Ensure the variable version contains a semantic versioned string

This file is read by the application at runtime if run as a module, and is also
read by the application build process to embed in the application details
"""

ex_installer_version = "0.0.5"

"""
Version history:

0.0.5 - Provide extra welcome information and instructions
      - Rephrase from "upload" to "load" which is potentially less confusing and more appropriate language
      - Refine Manage Arduino CLI text
      - Fix bug where navigating from Load screen crashes application due to missing version parameter
0.0.4 - Expose selected product version to product configuration view
      - Add application and product versions to generated config file
0.0.3 - Allow setting custom password for WiFi in AP mode
0.0.2 - Separate repository and version management from EX-CommandStation configuration
0.0.1 - Initial release:
      - Configure, compile, upload EX-CommandStation
      - Supports AVR, ESP32, and STM32
"""
