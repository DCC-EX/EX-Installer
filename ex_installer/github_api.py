"""
Module for downloading and extracting GitHub repositories

This model enables downloading and extracting GitHub repositories using threads and queues
"""

from github import Github
from threading import Thread, Lock
from collections import namedtuple
import sys
import os

if os.path.exists("token_file.py"):
    from .token_file import GitHubToken
from .file_manager import ThreadedDownloader, ThreadedExtractor, FileManager

QueueMessage = namedtuple("QueueMessage", ["status", "details"])


class ThreadedGitHubAPI(Thread):
    """
    Class for running GitHub API tasks in a separate thread
    """

    api_lock = Lock()

    def __init__(self, query, queue):
        super().__init__()
        self.query = query
        self.queue = queue

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", f"Run API query {self.query}")
        )
        with self.api_lock:
            try:
                output = self.query
                self.queue.put(
                    QueueMessage("success", output)
                )
            except Exception as error:
                self.queue.put(
                    QueueMessage("error", str(error))
                )


class GitHubAPI:
    """
    Class for downloading code from DCC-EX repositories
    """

    def __init__(self):
        if os.path.exists("token_file.py"):
            self.github_api = Github(GitHubToken.token)
        else:
            self.github_api = Github()

    def get_repo(self, repo_name):
        return self.github_api.get_repo(repo_name)

    def get_tags(self, repo, queue):
        thread = ThreadedGitHubAPI(repo.get_tags(), queue)
        thread.start()

    def download_archive(self, url, version, queue):
        if sys.platform.startswith("win"):
            archive_type = ".zip"
        else:
            archive_type = ".tar.gz"
        archive_name = version + archive_type
        target_name = os.path.join(FileManager.get_temp_dir(), archive_name)
        download_file = ThreadedDownloader(url + archive_name, target_name, queue)
        download_file.start()

    def extract_archive(self, archive, target_dir, queue):
        extracted = ThreadedExtractor(archive, target_dir, queue)
        extracted.start()
