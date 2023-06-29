"""
Module containing details for each product able to be installed with EX-Installer
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
            r"(^myHal\.cpp$)",
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
        "repo_name": "DCC-EX/EX-IOExpander",
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
