"""
Module for Arduino CLI management and interactions

This model can be used to download, install, configure, and update the Arduino CLI

This module uses threads and queues

© 2024, Peter Cole.
© 2023, Peter Cole.
All rights reserved.

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

import platform
import os
import sys
import tempfile
import subprocess
import json
from threading import Thread, Lock
from collections import namedtuple
import logging
from datetime import datetime, timedelta

from .file_manager import ThreadedDownloader, ThreadedExtractor


QueueMessage = namedtuple("QueueMessage", ["status", "topic", "data"])


@staticmethod
def get_exception(error):
    """
    Get an exception into text to add to the queue
    """
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(error).__name__, error.args)
    return message


class ThreadedArduinoCLI(Thread):
    """
    Class to run Arduino CLI commands in a separate thread, returning results to the provided queue

    There is a default timeout of 5 minutes (300 seconds) for any thread being started, after which
    they will be terminated

    Specifying the "time_limit" parameter will override this if necessary
    """

    arduino_cli_lock = Lock()

    def __init__(self, acli_path, params, queue, time_limit=300):
        """
        Initialise the object

        Need to provide:
        - full path the Arduino CLI executable/binary
        - a list of valid parameters
        - the queue instance to update
        """
        super().__init__()

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start thread")

        self.params = params
        self.process_params = [acli_path]
        self.process_params += self.params
        self.queue = queue
        self.time_limit = timedelta(seconds=time_limit)

    def run(self, *args, **kwargs):
        """
        Override for Thread.run()

        Creates a thread and executes with the provided parameters

        Results are placed in the provided queue object
        """
        start_time = datetime.now()
        self.queue.put(
            QueueMessage("info", "Run Arduino CLI", f"Arduino CLI parameters: {self.params}")
        )
        self.log.debug("Queue info %s", self.params)
        with self.arduino_cli_lock:
            try:
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.process = subprocess.Popen(self.process_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                startupinfo=startupinfo)
                self.output, self.error = self.process.communicate()
                self.log.debug(self.process_params)
            except Exception as error:
                self.queue.put(
                    QueueMessage("error", str(error), str(error))
                )
                self.log.error("Caught exception error: %s", str(error))
            if (self.time_limit is not None and ((datetime.now() - start_time) > self.time_limit)):
                self.queue.put(
                    QueueMessage("error", "The Arduino CLI command did not complete within the timeout period",
                                 f"The running Arduino CLI command took longer than {self.time_limit}")
                )
                self.log.error(f"The running Arduino CLI command took longer than {self.time_limit}")
                self.log.error(self.params)
                self.process.terminate()
            else:
                # Returncode 0 = success, anything else is an error
                topic = ""
                data = ""
                if self.error:
                    error = json.loads(self.error.decode())
                    topic = "Error in compile or upload"
                    data = ""
                    if "error" in error:
                        topic = str(error["error"])
                        data = str(error["error"])
                    if "output" in error:
                        if "stdout" in error["output"]:
                            if error["output"]["stdout"] != "":
                                data = str(error["output"]["stdout"] + "\n")
                        if "stderr" in error["output"]:
                            if error["output"]["stderr"] != "":
                                data += str(error["output"]["stderr"])
                    if data == "":
                        data = error
                else:
                    if self.output:
                        details = json.loads(self.output.decode())
                        if "success" in details:
                            if details["success"] is True:
                                topic = "Success"
                                data = details["compiler_out"]
                            else:
                                topic = details["error"]
                                data = details["compiler_err"]
                        else:
                            topic = "Success"
                            if "stdout" in details:
                                data = details["stdout"]
                            else:
                                data = details
                    else:
                        topic = "No output"
                        data = "No output"
                if self.process.returncode == 0:
                    status = "success"
                    self.log.debug(data)
                else:
                    status = "error"
                    self.log.error(data)
                self.queue.put(
                    QueueMessage(status, topic, data)
                )


class ArduinoCLI:
    """
    Class for the Arduino CLI model

    This class exposes the various methods to interact with the Arduino CLI including:

    - cli_file_path() - returns the full file path to where the Arduino CLI should reside
    - is_installed() - checks the CLI is installed and executable, returns True/False
    - get_version() - gets the Arduino CLI version, returns to the provided queue
    - get_platforms() - gets the list of installed platforms
    - download_cli() - downloads the appropriate CLI for the operating system, returns the file path
    - install_cli() - extracts the CLI to the specified file path from download file path
    - initialise_config() - adds additional URLs to the CLI config
    - update_index() - performs the core update-index and initial board list
    - get_package_list() - gets the list of platform packages to install
    - install_package() - installs the provided packages
    - upgrade_platforms() - performs the core upgrade to ensure all are up to date
    - list_boards() - lists all connected boards, returns list of dictionaries for boards
    - upload_sketch() - compiles and uploads the provided sketch to the provided device
    """

    # Dictionary of Arduino CLI archives for the appropriate platform
    arduino_downloads = {
        "Linux64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz",
        "Darwin64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz",
        "Windows32": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_32bit.zip",
        "Windows64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
    }

    # Dictionary for additional board/platform support for the Arduino CLI
    extra_platforms = {
        "Espressif ESP32": {
            "platform_id": "esp32:esp32@2.0.17",
            "url": "https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json"
        },
        "STMicroelectronics Nucleo/STM32": {
            "platform_id": "STMicroelectronics:stm32",
            "url": "https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json"
        }
    }

    # Dictionary of devices supported with EX-Installer to enable selection when detecting unknown devices
    supported_devices = {
        "Arduino Mega or Mega 2560": "arduino:avr:mega",
        "Arduino Uno": "arduino:avr:uno",
        "Arduino Nano": "arduino:avr:nano",
        "DCC-EX EX-CSB1": "esp32:esp32:esp32",
        "ESP32 Dev Kit": "esp32:esp32:esp32",
        "STMicroelectronics Nucleo F411RE": "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F411RE",
        "STMicroelectronics Nucleo F446RE": "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F446RE"
    }

    # Dictionary of DCC-EX specific devices, used to preselect or exclude motor definitions
    dccex_devices = {
        "DCC-EX EX-CSB1": "EXCSB1"
    }

    def __init__(self, selected_device=None):
        """
        Initialise the Arduino CLI instance

        The instance retains the current list of detected devices and the current selected device (if any)
        """
        self.selected_device = selected_device
        self.detected_devices = []
        self.dccex_device = None

        # Set up logger
        self.log = logging.getLogger(__name__)

    def cli_file_path(self):
        """
        Function to get the full path and filename of the Arduino CLI.

        Cross-platform, returns the full file path or False if there is an error.

        For example:
        - Linux - /home/<user>/ex-installer/arduino-cli/arduino-cli
        - Windows - C:\\Users\\<user>\\ex-installer\\arduino-cli\\arduino-cli.exe
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            _result = False
            self.log.debug("Unsupported operating system")
        else:
            if platform.system() == "Windows":
                _cli = "arduino-cli.exe"
            else:
                _cli = "arduino-cli"
            if os.path.expanduser("~"):
                _cli_path = os.path.join(
                    os.path.expanduser("~"),
                    "ex-installer",
                    "arduino-cli",
                    _cli
                )
                _result = _cli_path.replace("\\", "\\\\")   # Need to do this for Windows
                self.log.debug(_result)
            else:
                raise ValueError("Could not obtain user home directory")
                _result = False
                self.log.error("Could not obtain user home directory")
        return _result

    def is_installed(self, file_path):
        """
        Function to check if the Arduino CLI in installed in the provided file path

        Also checks to ensure it is executable.

        Returns True or False
        """
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            _result = True
        else:
            _result = False
        self.log.debug(_result)
        return _result

    def get_version(self, file_path, queue):
        """
        Function to retrieve the version of the Arduino CLI

        If obtaining the version is successful it will be in the queue's "data" field
        """
        if self.is_installed(file_path):
            params = ["version", "--format", "jsonmini"]
            acli = ThreadedArduinoCLI(file_path, params, queue)
            acli.start()
        else:
            queue.put(
                QueueMessage("error", "Arduino CLI is not installed", "Arduino CLI is not installed")
            )
            self.log.debug("Arduino CLI not installed")

    def get_platforms(self, file_path, queue):
        """
        Function to retrieve the current platforms installed with the Arduino CLI

        If successful, the list will be in the queue's "data" field
        """
        if self.is_installed(file_path):
            params = ["core", "list", "--format", "jsonmini"]
            acli = ThreadedArduinoCLI(file_path, params, queue)
            acli.start()
        else:
            queue.put(
                QueueMessage("error", "Arduino CLI is not installed", "Arduino CLI is not installed")
            )
            self.log.debug("Arduino CLI not installed")

    def download_cli(self, queue):
        """
        Download the Arduino CLI

        If successful, the archive's path will be in the queue's "data" field

        If error, the error will be in the queue's "data" field
        """
        if not platform.system():
            self.log.error("Unsupported operating system")
            queue.put(
                QueueMessage("error", "Unsupported operating system", "Unsupported operating system")
            )
        else:
            if sys.maxsize > 2**32:
                _installer = platform.system() + "64"
            else:
                _installer = platform.system() + "32"
            self.log.debug(_installer)
            if _installer in ArduinoCLI.arduino_downloads:
                _target_file = os.path.join(
                    tempfile.gettempdir(),
                    ArduinoCLI.arduino_downloads[_installer].split("/")[-1]
                )
                download = ThreadedDownloader(ArduinoCLI.arduino_downloads[_installer], _target_file, queue)
                download.start()
            else:
                self.log.error("No Arduino CLI available for this operating system")
                queue.put(
                    QueueMessage("error", "No Arduino CLI available for this operating system",
                                 "No Arduino CLI available for this operating system")
                )

    def install_cli(self, download_file, file_path, queue):
        """
        Install the Arduino CLI by extracting to the specified directory
        """
        cli_directory = os.path.dirname(file_path)
        if not os.path.exists(cli_directory):
            try:
                os.makedirs(cli_directory)
            except Exception as error:
                message = get_exception(error)
                self.log.error(message)
                queue.put(
                    QueueMessage("error", "Could not create Arduino CLI directory", message)
                )
                return
        extract = ThreadedExtractor(download_file, cli_directory, queue)
        extract.start()

    def add_url_config(self, file_path, queue):
        """
        Adds extra URLs to the Arduino CLI configuration
        """
        params = ["config", "add", "--format", "jsonmini", "board_manager.additional_urls"]
        if len(self.extra_platforms) > 0:
            for extra_platform in self.extra_platforms:
                acli = ThreadedArduinoCLI(file_path,
                                          params + [self.extra_platforms[extra_platform]["url"]],
                                          queue)
                acli.start()

    def initialise_config(self, file_path, queue):
        """
        Initialises the Arduino CLI configuration with the provided additional boards

        Overwrites existing configuration options
        """
        params = ["config", "init", "--format", "jsonmini", "--overwrite"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()
        self.add_url_config(file_path, queue)

    def update_index(self, file_path, queue):
        """
        Update the Arduino CLI core index
        """
        params = ["core", "update-index", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def get_package_list(self, file_path, queue):
        """
        Get list of Arduino packages to install
        """
        params = ["core", "list", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def install_package(self, file_path, package, queue):
        """
        Install packages for the listed Arduino platforms
        """
        self.add_url_config(file_path, queue)
        params = ["core", "install", package, "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue, 600)
        acli.start()

    def upgrade_platforms(self, file_path, queue):
        """
        Upgrade Arduino CLI platforms
        """
        self.add_url_config(file_path, queue)
        params = ["core", "upgrade", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def install_library(self, file_path, library, queue):
        """
        Install the specified Arduino library
        """
        params = ["lib", "install", library, "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def list_boards(self, file_path, queue):
        """
        Returns a list of attached boards
        """
        params = ["board", "list", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue, 120)
        acli.start()

    def upload_sketch(self, file_path, fqbn, port, sketch_dir, queue):
        """
        Compiles and uploads the sketch in the specified directory to the provided board/port
        """
        params = ["upload", "-v", "-t", "-b", fqbn, "-p", port, sketch_dir, "--format", "jsonmini"]
        if fqbn.startswith('esp32:esp32'):
            params = params + [ "--board-options", "UploadSpeed=115200" ]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def compile_sketch(self, file_path, fqbn, sketch_dir, queue):
        """
        Compiles the sketch ready to upload
        """
        params = ["compile", "-b", fqbn, sketch_dir, "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()
