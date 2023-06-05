"""
Module for a Git client using the pygit2 module

This model enables cloning and selecting versions from GitHub repositories using threads and queues
"""

# Import Python modules
import pygit2
from threading import Thread, Lock
from collections import namedtuple
import os

QueueMessage = namedtuple("QueueMessage", ["status", "topic", "data"])


class ThreadedGitClient(Thread):
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


class GitClient:
    """
    Class for cloning code and selecting specific versions from DCC-EX repositories
    """

    def get_repo(self, repo_dir):
        """
        Validate the provided directory is a repo and return if it is
        """
        repo = False
        if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
            repo = pygit2.Repository(pygit2.discover_repository(repo_dir))
            if isinstance(repo, pygit2.Repository):
                print("Repo")
            else:
                print("Not repo")
        return repo

    def validate_repo(self, repo, remote):
        """
        Function to validate repo is still using the provided remote

        Returns True (remote still valid) or False (remote invalid or multiple)
        """
        pass

    def check_local_changes(self, remote):
        """
        Function to check for local changes to files

        Returns False (no changes) or a list of changed files
        """
        pass
