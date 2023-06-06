"""
Module for file management

Downloading, extracting
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


QueueMessage = namedtuple("QueueMessage", ["status", "topic", "data"])


class ThreadedDownloader(Thread):

    download_lock = Lock()

    def __init__(self, url, target, queue):
        super().__init__()
        self.url = url
        self.target = target
        self.queue = queue

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Downloading {self.url}", f"Downloading {self.url}")
        )
        with self.download_lock:
            _response = requests.get(self.url, stream=True)
            if _response.status_code == 200:
                try:
                    with open(self.target, "wb") as _file:
                        _file.write(_response.raw.read())
                    self.queue.put(
                        QueueMessage("success", "Downloaded successfully", self.target)
                    )
                    print("Success")
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Download error", str(error))
                    )
            else:
                self.queue.put(
                    QueueMessage("error", "Download error",
                                 f"Downloading failed with status code {_response.status_code}: {_response.text}")
                )


class ThreadedExtractor(Thread):

    extractor_lock = Lock()

    def __init__(self, archive_file, target_dir, queue):
        super().__init__()
        self.archive_file = archive_file
        self.target_dir = target_dir
        self.queue = queue

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Extracting {self.archive_file}", f"Extracting {self.archive_file}")
        )
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
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Extraction error", str(error))
                    )
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
                except Exception as error:
                    self.queue.put(
                        QueueMessage("error", "Extraction error", str(error))
                    )


class FileManager:
    """
    Class for managing files and directories
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_base_dir():
        """
        Returns the base directory for EX-Installer
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            return False
        else:
            if os.path.expanduser("~"):
                _cli_path = os.path.join(
                    os.path.expanduser("~"),
                    "ex-installer",
                )
                if sys.platform.startswith("win"):
                    return _cli_path.replace("\\", "\\\\")
                else:
                    return _cli_path
            else:
                raise ValueError("Could not obtain user home directory")
                return False

    @staticmethod
    def get_install_dir(product_name):
        """
        Returns the path to extract software into
        """
        if FileManager.get_base_dir():
            dir = os.path.join(FileManager.get_base_dir().replace("\\\\", "\\"), product_name)
            if sys.platform.startswith("win"):
                return dir.replace("\\", "\\\\")
            else:
                return dir
        else:
            return False

    @staticmethod
    def get_temp_dir():
        """
        Returns the temp directory
        """
        if not platform.system():
            raise ValueError("Unsupported operating system")
            return False
        else:
            if tempfile.gettempdir():
                return tempfile.gettempdir()
            else:
                raise ValueError("Unable to determine temp directory")
                return False

    @staticmethod
    def rename_dir(source_dir, target_dir):
        if os.path.exists(source_dir):
            if not os.path.exists(target_dir):
                os.rename(source_dir, target_dir)
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def read_version(version_file):
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

        Pattern list must contain a valid Python regular expression with grouping
        A match is made on one group only (group 1)
        """
        if os.path.exists(dir):
            config_files = []
            for file in os.listdir(dir):
                for pattern in pattern_list:
                    file_match = re.search(pattern, file)
                    if file_match:
                        filename = file_match[1]
                        if filename:
                            config_files.append(filename)
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
        try:
            file = open(file_path, "w", encoding="utf-8")
            for line in contents:
                file.write(line)
            file.close()
            return file_path
        except Exception as error:
            return str(error)
