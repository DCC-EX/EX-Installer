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


@staticmethod
def get_exception(error):
    """
    Get an exception into text to add to the queue
    """
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(error).__name__, error.args)
    return message


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

        Returns a tuple of (True|False, None|message)
        """
        git_file = os.path.join(repo_dir, ".git")
        if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
            if os.path.exists(git_file):
                try:
                    repo = pygit2.Repository(git_file)
                except Exception as error:
                    message = get_exception(error)
                else:
                    if isinstance(repo, pygit2.Repository):
                        return repo
                    else:
                        return False
            else:
                return False, ("Directory is not a Git repository")
        else:
            message("Directory does not exist")
            return False, message

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
    
    def clone_repo(repo_url, repo_dir):
        """
        Clone a remote repo using a separate thread

        Returns the repo instance if successful
        """

