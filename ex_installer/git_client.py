"""
Module for a Git client using the pygit2 module

This model enables cloning and selecting versions from GitHub repositories using threads and queues
"""

# Import Python modules
import pygit2
from threading import Thread, Lock
from collections import namedtuple
import os
from pprint import pprint

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

    @staticmethod
    def get_repo(repo_dir):
        """
        Validate the provided directory is a repo

        Returns repo object or False if not a repo
        """
        if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
            repo = pygit2.Repository(pygit2.discover_repository(repo_dir))
            if isinstance(repo, pygit2.Repository):
                return repo
            else:
                return False
        else:
            return False

    @staticmethod
    def validate_remote(repo, repo_url):
        """
        Function to validate repo is still using the provided remote URL for the origin

        Returns a list of (True|False, Details of error)
        """
        is_valid = False
        details = ""
        if isinstance(repo, pygit2.Repository):
            if len(list(repo.remotes)) == 1:
                remote = repo.remotes[0]
                if remote.name == "origin" and remote.url == repo_url:
                    is_valid = True
                else:
                    details = f"Remote GitHub repository is invalid (Remote {remote.name}: URL {remote.url})"
            else:
                details = "More than one remotes are in use"
        else:
            details = f"{repo} is not a valid Git repository"
        return (is_valid, details)

    @staticmethod
    def check_local_changes(repo):
        """
        Function to check for local changes to files in the provided repo

        Returns False (no changes) or a list of changed files
        """
        file_list = None
        if isinstance(repo, pygit2.Repository):
            if len(repo.status()) > 0:
                file_list = []
                status = repo.status()
                for file, flag in status.items():
                    change = "Unknown"
                    if flag == pygit2.GIT_STATUS_WT_NEW:
                        change = "Added"
                    elif flag == pygit2.GIT_STATUS_WT_DELETED:
                        change = "Deleted"
                    elif flag == pygit2.GIT_STATUS_WT_MODIFIED:
                        change = "Modified"
                    file_list.append(file + " (" + change + ")")
        else:
            file_list = [f"{repo} is not a valid repository"]
        return file_list

    @staticmethod
    def validate_local_repo(local_dir, remote_url):
        """
        Function to validate a local repository is ok to use, checks:

        - if the product directory is already a cloned repo
        - if the cloned repo is configured correctly
        - any locally modified files that would interfere with Git commands

        Returns a list of (True|False, Details)

        True = repo is good to use
        False = repo has issues
        Details = empty for no issues, otherwise string of issue details
        """
        repo = GitClient.get_repo(local_dir)
        status = False
        details = ""
        if repo:
            validate_remote = GitClient.validate_remote(repo, remote_url)
            if validate_remote[0]:
                local_changes = GitClient.check_local_changes(repo)
                if not local_changes:
                    status = True
                else:
                    details = "Repository has unstaged local change(s): " + ", ".join(local_changes)
            else:
                details = (validate_remote[1])
        else:
            details(f"{local_dir} is not a valid Git repository")
        return (status, details)
