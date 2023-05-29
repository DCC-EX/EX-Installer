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


QueueMessage = namedtuple("QueueMessage", ["status", "details"])


class ThreadedArduinoCLI(Thread):

    arduino_cli_lock = Lock()

    def __init__(self, acli_path, params, queue):
        super().__init__()
        self.params = params
        self.process_params = [acli_path]
        self.process_params += self.params
        self.queue = queue

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Arduino CLI parameters: {self.params}")
        )
        with self.arduino_cli_lock:
            try:
                self.process = subprocess.Popen(self.process_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.output, self.error = self.process.communicate()
            except Exception as error:
                self.queue.put(
                    QueueMessage("error", str(error))
                )
            if self.error:
                self.queue.put(
                    QueueMessage("error", json.loads(self.error.decode()))
                )
            else:
                if self.output:
                    details = json.loads(self.output.decode())
                    if "success" in details:
                        if details["success"] is True:
                            status = "success"
                        else:
                            status = "error"
                            details = details["error"]
                            if "compiler_err" in details:
                                print(details["compiler_err"])
                    else:
                        status = "success"
                else:
                    status = "success"
                    details = "No output"
                self.queue.put(
                    QueueMessage(status, details)
                )


class ArduinoCLI:
    """
    Class for the Arduino CLI model

    This class exposes the various methods to interact with the Arduino CLI including:

    - get_cli_file() - returns the full file path to where the Arduino CLI should reside
    - is_installed(<path to cli>) - checks the CLI is installed and executable, returns True/False
    - download_cli() - downloads the appropriate CLI for the operating system, returns the file path
    - install_cli(<download>, <path to cli>) - extracts the CLI to the specified file path from download file path
    - upgrade_platforms(<path to cli>) - performs the core upgrade to ensure all are up to date
    - init_config(<path to cli>) - adds additional URLs to the CLI config
    - update_index(<path to cli>) - performs the core update-index and initial board list
    - install_packages(<path to cli>) - installs the packages for for all boards including extras
    - list_boards(<path to cli>) - lists all connected boards, returns list of dictionaries for boards
    """
    arduino_downloads = {
        "Linux32": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_32bit.tar.gz",
        "Linux64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz",
        "macOS64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz",
        "Windows32": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_32bit.zip",
        "Windows64": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
    }

    extra_boards = [
        "https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json",
        "https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json"
    ]

    extra_platforms = {
        "Espressif ESP32": "esp32:esp32",
        "STMicroelectronics Nucleo/STM32": "STMicroelectronics:stm32"
    }

    def __init__(self, selected_device=None):
        self.selected_device = selected_device
        self.detected_devices = None

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
        """
        if self.is_installed(file_path):
            params = ["version", "--format", "jsonmini"]
            acli = ThreadedArduinoCLI(file_path, params, queue)
            acli.start()
        else:
            queue.put(
                QueueMessage("error", "Arduino CLI is not installed")
            )

    def download_cli(self, queue):
        """
        Download the Arduino CLI
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
        if len(self.extra_boards) > 0:
            _url_list = ",".join(self.extra_boards)
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
