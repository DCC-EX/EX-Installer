"""
Module containing details for each product able to be installed with EX-Installer

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

from . import images

product_details = {
    "ex_commandstation": {
        "product_name": "EX-CommandStation",
        "product_logo": images.EX_COMMANDSTATION_LOGO,
        "repo_name": "DCC-EX/CommandStation-EX",
        "default_branch": "master",
        "repo_url": "https://github.com/DCC-EX/CommandStation-EX.git",
        "supported_devices": [
            "arduino:avr:uno",
            "arduino:avr:nano",
            "arduino:avr:nano:cpu=atmega328",
            "arduino:avr:mega",
            "esp32:esp32:esp32",
            "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F411RE",
            "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F446RE"
        ],
        "minimum_config_files": [
            "config.h"
        ],
        "other_config_files": [
            r"^my.*\.[^?]*example\.cpp$|(^my.*\.cpp$)",
            r"^my.*\.[^?]*example\.h$|(^my.*\.h$)"
        ]
    },
    "ex_ioexpander": {
        "product_name": "EX-IOExpander",
        "product_logo": images.EX_IOEXPANDER_LOGO,
        "repo_name": "DCC-EX/EX-IOExpander",
        "default_branch": "main",
        "repo_url": "https://github.com/DCC-EX/EX-IOExpander.git",
        "supported_devices": [
            "arduino:avr:uno",
            "arduino:avr:nano",
            "arduino:avr:nano:cpu=atmega328",
            "arduino:avr:mega",
            "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F411RE"
        ],
        "minimum_config_files": [
            "myConfig.h"
        ]
    },
    "ex_turntable": {
        "product_name": "EX-Turntable",
        "product_logo": images.EX_TURNTABLE_LOGO,
        "repo_name": "DCC-EX/EX-Turntable",
        "default_branch": "main",
        "repo_url": "https://github.com/DCC-EX/EX-Turntable.git",
        "supported_devices": [
            "arduino:avr:uno",
            "arduino:avr:nano",
            "arduino:avr:nano:cpu=atmega328"
        ],
        "minimum_config_files": [
            "config.h"
        ]
    }
}
