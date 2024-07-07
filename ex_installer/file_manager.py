"""
Module for file management

Downloading, extracting

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
import requests
import tarfile
from zipfile import ZipFile, Path
from threading import Thread, Lock
from collections import namedtuple
import re
import shutil
import logging
import json


QueueMessage = namedtuple("QueueMessage", ["status", "topic", "data"])


class ThreadedDownloader(Thread):

    download_lock = Lock()

    def __init__(self, url, target, queue):
        super().__init__()
        self.url = url
        self.target = target
        self.queue = queue

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Downloading {self.url}", f"Downloading {self.url}")
        )
        self.log.debug(self.url)
        with self.download_lock:
            _response = requests.get(self.url, stream=True)
            if _response.status_code == 200:
                try:
                    with open(self.target, "wb") as _file:
                        _file.write(_response.raw.read())
                    self.queue.put(
                        QueueMessage("success", "Downloaded successfully", self.target)
                    )
                    self.log.debug(self.target)
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Download error", str(error))
                    )
                    self.log.error(str(error))
            else:
                self.queue.put(
                    QueueMessage("error", "Download error",
                                 f"Downloading failed with status code {_response.status_code}: {_response.text}")
                )
                self.log.error("Error %s: %s", _response.status_code, _response.text)


class ThreadedExtractor(Thread):

    extractor_lock = Lock()

    def __init__(self, archive_file, target_dir, queue):
        super().__init__()
        self.archive_file = archive_file
        self.target_dir = target_dir
        self.queue = queue

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Extracting {self.archive_file}", f"Extracting {self.archive_file}")
        )
        self.log.debug(self.archive_file)
        with self.extractor_lock:
            if platform.system() == "Windows":
                relpath = None
                try:
                    with ZipFile(self.archive_file) as archive:
                        for item in Path(archive).iterdir():
                            if item.is_dir():
                                relpath, = Path(archive).iterdir()
                        archive.extractall(self.target_dir)
                    if relpath:
                        dir_name = os.path.join(self.target_dir.replace("\\\\", "\\"), relpath.name)
                    else:
                        dir_name = self.target_dir
                    self.queue.put(
                        QueueMessage("success", "Extraction successful", dir_name)
                    )
                    self.log.debug(dir_name)
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Extraction error", str(error))
                    )
                    self.log.error(str(error))
            else:
                try:
                    archive = tarfile.open(self.archive_file)
                    relpath = os.path.commonprefix(archive.getnames())
                    if len(relpath) > 0:
                        dir_name = os.path.join(self.target_dir, relpath)
                    else:
                        dir_name = self.target_dir
                    archive.extractall(self.target_dir)
                    archive.close()
                    self.queue.put(
                        QueueMessage("success", "Extraction successful", dir_name)
                    )
                    self.log.debug(dir_name)
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Extraction error", str(error))
                    )
                    self.log.error(str(error))


class FileManager:
    """
    Class for managing files and directories
    """
    # Set up logger
    log = logging.getLogger(__name__)

    # User preferences directory and file name
    user_preference_dir = "user-config"
    user_preference_file = "ex-installer-preferences.json"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_base_dir():
        """
        Returns the base directory for EX-Installer
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            FileManager.log.error("Unsupported operating system")
            return False
        else:
            if os.path.expanduser("~"):
                _cli_path = os.path.join(
                    os.path.expanduser("~"),
                    "ex-installer",
                )
                if sys.platform.startswith("win"):
                    _cli_path = _cli_path.replace("\\", "\\\\")
                FileManager.log.debug(_cli_path)
                return _cli_path
            else:
                raise ValueError("Could not obtain user home directory")
                FileManager.log.error("Could not obtain user home directory")
                return False

    @staticmethod
    def get_install_dir(product_name):
        """
        Returns the path to extract software into
        """
        if FileManager.get_base_dir():
            dir = os.path.join(FileManager.get_base_dir().replace("\\\\", "\\"), product_name)
            if sys.platform.startswith("win"):
                dir = dir.replace("\\", "\\\\")
            FileManager.log.debug(dir)
            return dir
        else:
            FileManager.log.error("Could not obtain installation directory")
            return False

    @staticmethod
    def get_temp_dir():
        """
        Returns the temp directory
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            FileManager.log.error("Unsupported operating system")
            return False
        else:
            if tempfile.gettempdir():
                FileManager.log.debug(tempfile.gettempdir())
                return tempfile.gettempdir()
            else:
                raise ValueError("Unable to determine temp directory")
                FileManager.log.error("Unable to determine temp directory")
                return False

    @staticmethod
    def rename_dir(source_dir, target_dir):
        if os.path.exists(source_dir):
            if not os.path.exists(target_dir):
                try:
                    os.rename(source_dir, target_dir)
                except Exception as error:
                    FileManager.log.error(str(error))
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

    @staticmethod
    def read_version(version_file):
        """
        Function to read a version string from a file

        Not recommended over obtaining versions from GitHub tags, however can be used if those are not defined
        Returns False if no version defined, or a string containing the version
        """
        if os.path.exists(version_file):
            fo = open(version_file, "r", encoding="utf-8")
            for line in fo:
                print(line)
            fo.close()
        else:
            return False

    @staticmethod
    def get_config_files(dir, pattern_list):
        """
        Function to check for the existence of existing configuration files

        Returns False if no files, otherwise a list of file names matching the provided list of patterns

        Pattern list can contain either:
        - a valid Python regular expression with grouping, where a match is made on one group only (group 1)
        - a file name

        This is a valid example of a pattern: r"^my.*\.[^?]*example\.h$|(^my.*\.h$)"  # noqa: W605
        This is an invalid example of a pattern: r"^config\.h$"  # noqa: W605
        This would be valid, but better to just provide filename: r"^(config\.h)$"  # noqa: W605
        """
        if os.path.exists(dir):
            config_files = []
            for file in os.listdir(dir):
                for pattern in pattern_list:
                    file_match = re.search(pattern, file)
                    if file_match and len(file_match.groups()) > 0:
                        filename = file_match[1]
                        if filename:
                            config_files.append(filename)
                    elif file == pattern:
                        config_files.append(file)
            return config_files
        else:
            return False

    @staticmethod
    def get_filepath(dir, filename):
        return os.path.join(dir, filename)

    @staticmethod
    def get_list_from_file(file_path, pattern):
        match_list = []
        if os.path.exists(file_path):
            file = open(file_path, "r", encoding="utf-8")
            for line in file:
                match = re.search(pattern, line)
                if match:
                    option = match[1]
                    if option not in match_list:
                        match_list.append(option)
            return match_list
        else:
            return False

    @staticmethod
    def write_config_file(file_path, contents):
        """Function to write the list of contents to a config file

        Pass the full path to the file and the list of lines to write
        Writes utf-8 encoded

        Returns the same file path if successful, otherwise the exception error message
        """
        try:
            file = open(file_path, "w", encoding="utf-8")
            for line in contents:
                file.write(line)
            file.close()
            return file_path
        except Exception as error:
            return str(error)

    @staticmethod
    def read_config_file(file_path):
        """Function to read and return file contents
        Pass the full path to the file
        Returns the text from the file path if successful, otherwise the exception error message
        """
        try:
            file = open(file_path, "r", encoding="utf-8")
            lines = file.read()
            file.close()
            return lines
        except Exception as error:
            return str(error)

    @staticmethod
    def dir_is_empty(dir):
        """
        Check if directory is empty

        Returns True if so, False if not
        """
        if os.listdir(dir) > 0:
            return False
        else:
            return True

    @staticmethod
    def copy_config_files(source_dir, dest_dir, file_list):
        """
        Copy the specified list of files from source to destination directory

        Returns None if successful, otherwise a list of files that failed to copy
        """
        failed_files = []
        for file in file_list:
            source = os.path.join(source_dir, file)
            dest = os.path.join(dest_dir, file)
            try:
                shutil.copy(source, dest)
            except Exception:
                failed_files.append(file)
        if len(failed_files) > 0:
            return failed_files
        else:
            return None

    @staticmethod
    def delete_config_files(dir, file_list):
        """
        Delete the specified list of files from sepcified directory

        Returns None if successful, otherwise a list of files that failed to copy
        """
        failed_files = []
        for file_name in file_list:
            file = os.path.join(dir, file_name)
            try:
                os.remove(file)
            except Exception:
                failed_files.append(file_name)
        if len(failed_files) > 0:
            return failed_files
        else:
            return None

    @staticmethod
    def is_valid_dir(dir):
        """
        Simply checks directory exists and that it is a directory

        Returns True or False
        """
        if os.path.exists(dir) and os.path.isdir(dir):
            return True
        else:
            return False

    @staticmethod
    def save_user_preferences(preferences):
        """
        Method to save user preferences to the user preference file

        Call this method with the user preferences dictionary, which will save these
        """
        user_dir = os.path.join(FileManager.get_base_dir(), FileManager.user_preference_dir)
        if not os.path.isdir(user_dir):
            try:
                os.mkdir(user_dir)
            except Exception as dir_error:
                FileManager.log.error(f"Could not create user preferences directory {user_dir}")
                FileManager.log.error(dir_error)
        if isinstance(preferences, dict):
            user_file = os.path.join(FileManager.get_base_dir(), FileManager.user_preference_dir,
                                     FileManager.user_preference_file)
            try:
                with open(user_file, "w") as file_handle:
                    json.dump(preferences, file_handle)
            except Exception as file_error:
                FileManager.log.error(f"Unable to write to user preferences file {user_file}")
                FileManager.log.error(preferences)
                FileManager.log.error(file_error)

    @staticmethod
    def get_user_preferences():
        """
        Method to the dictionary of user preferences

        Reads the JSON user preference file and returns the dictionary
        """
        preferences = {}
        user_file = os.path.join(FileManager.get_base_dir(), FileManager.user_preference_dir,
                                 FileManager.user_preference_file)
        if os.path.isfile(user_file):
            try:
                with open(user_file, "r") as file_handle:
                    preferences = json.load(file_handle)
            except Exception as file_error:
                FileManager.log.error(f"Unable to read user preferences from file {user_file}")
                FileManager.log.error(file_error)
        return preferences
