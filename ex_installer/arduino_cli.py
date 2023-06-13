"""
Module for Arduino CLI management and interactions

This model can be used to download, install, configure, and update the Arduino CLI

This module uses threads and queues
"""

import platform
import os
import sys
import tempfile
import subprocess
import json
from threading import Thread, Lock
from collections import namedtuple

from .file_manager import ThreadedDownloader, ThreadedExtractor


QueueMessage = namedtuple("QueueMessage", ["status", "topic", "data"])


class ThreadedArduinoCLI(Thread):
    """
    Class to run Arduino CLI commands in a separate thread, returning results to the provided queue
    """

    arduino_cli_lock = Lock()

    def __init__(self, acli_path, params, queue):
        """
        Initialise the object

        Need to provide:
        - full path the Arduino CLI executable/binary
        - a list of valid parameters
        - the queue instance to update
        """
        super().__init__()
        self.params = params
        self.process_params = [acli_path]
        self.process_params += self.params
        self.queue = queue

    def run(self, *args, **kwargs):
        """
        Override for Thread.run()

        Creates a thread and executes with the provided parameters

        Results are placed in the provided queue object
        """
        self.queue.put(
            QueueMessage("info", "Run Arduino CLI", f"Arduino CLI parameters: {self.params}")
        )
        with self.arduino_cli_lock:
            try:
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.process = subprocess.Popen(self.process_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                startupinfo=startupinfo)
                self.output, self.error = self.process.communicate()
            except Exception as error:
                self.queue.put(
                    QueueMessage("error", str(error), str(error))
                )
            if self.error:
                self.queue.put(
                    QueueMessage("error", json.loads(self.error.decode()), json.loads(self.error.decode()))
                )
            else:
                if self.output:
                    details = json.loads(self.output.decode())
                    if "success" in details:
                        if details["success"] is True:
                            status = "success"
                            topic = "Success"
                            data = details["compiler_out"]
                        else:
                            status = "error"
                            topic = details["error"]
                            data = details["compiler_err"]
                    else:
                        status = "success"
                        topic = "Success"
                        data = details
                else:
                    status = "success"
                    topic = "Error"
                    data = "No output"
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
        "Linux32": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_32bit.tar.gz",
        "Linux64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz",
        "macOS64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz",
        "Windows32": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_32bit.zip",
        "Windows64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
    }

    # Dictionary for additional board/platform support for the Arduino CLI
    extra_platforms = {
        "Espressif ESP32": {
            "platform_id": "esp32:esp32",
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
        "Arduino Nano (Old bootloader)": "arduino:avr:nano:cpu=atmega328",
        "ESP32 Dev Kit": "esp32:esp32:esp32",
        "STMicroelectronics Nucleo F411RE": "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F411RE",
        "STMicroelectronics Nucleo F446RE": "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F446RE"
    }

    def __init__(self, selected_device=None):
        """
        Initialise the Arduino CLI instance

        The instance retains the current list of detected devices and the current selected device (if any)
        """
        self.selected_device = selected_device
        self.detected_devices = []

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
            else:
                raise ValueError("Could not obtain user home directory")
                _result = False
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

    def download_cli(self, queue):
        """
        Download the Arduino CLI

        If successful, the archive's path will be in the queue's "data" field

        If error, the error will be in the queue's "data" field
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            _result = False
        else:
            if sys.maxsize > 2**32:
                _installer = platform.system() + "64"
            else:
                _installer = platform.system() + "32"
            if _installer in ArduinoCLI.arduino_downloads:
                _target_file = os.path.join(
                    tempfile.gettempdir(),
                    ArduinoCLI.arduino_downloads[_installer].split("/")[-1]
                )
                download = ThreadedDownloader(ArduinoCLI.arduino_downloads[_installer], _target_file, queue)
                download.start()
                _result = True
            else:
                raise ValueError("Sorry but there is no Arduino CLI available for this operating system")
                _result = False
        return _result

    def install_cli(self, download_file, file_path, queue):
        """
        Install the Arduino CLI by extracting to the specified directory
        """
        cli_directory = os.path.dirname(file_path)
        if not os.path.exists(cli_directory):
            os.makedirs(cli_directory)
        extract = ThreadedExtractor(download_file, cli_directory, queue)
        extract.start()

    def initialise_config(self, file_path, queue):
        """
        Initialises the Arduino CLI configuration with the provided additional boards

        Overwrites existing configuration options
        """
        params = ["config", "init", "--format", "jsonmini", "--overwrite"]
        if len(self.extra_platforms) > 0:
            platform_list = []
            for extra_platform in self.extra_platforms:
                platform_list.append(self.extra_platforms[extra_platform]["url"])
            _url_list = ",".join(platform_list)
            params += ["--additional-urls", _url_list]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

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
        params = ["core", "install", package, "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def upgrade_platforms(self, file_path, queue):
        """
        Upgrade Arduino CLI platforms
        """
        params = ["core", "upgrade", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def list_boards(self, file_path, queue):
        """
        Returns a list of attached boards
        """
        params = ["board", "list", "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()

    def upload_sketch(self, file_path, fqbn, port, sketch_dir, queue):
        """
        Compiles and uploads the sketch in the specified directory to the provided board/port
        """
        params = ["compile", "-b", fqbn, "-u", "-t", "-p", port, sketch_dir, "--format", "jsonmini"]
        acli = ThreadedArduinoCLI(file_path, params, queue)
        acli.start()
