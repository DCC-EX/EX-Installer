"""
Module for a Git client using the pygit2 module

This model enables cloning and selecting versions from GitHub repositories using threads and queues
"""

# Import Python modules
import pygit2
from threading import Thread, Lock
from collections import namedtuple, OrderedDict
import os
import re
import logging

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
    Class for running pygit2 tasks in a separate thread
    """

    api_lock = Lock()

    def __init__(self, task_name, task, queue, *args):
        super().__init__()
        self.task_name = task_name
        self.task = task
        self.queue = queue
        self.args = args

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Create instance")

    def run(self, *args, **kwargs):
        self.queue.put(
            QueueMessage("info", self.task_name, f"Run pygit2 task {str(self.task)} with params {self.args}")
        )
        self.log.debug("Queue info run %s with params %s", str(self.task), self.args)
        with self.api_lock:
            try:
                output = self.task(*self.args)
                self.queue.put(
                    QueueMessage("success", self.task_name, output)
                )
                self.log.debug("Success: %s", output)
            except Exception as error:
                message = get_exception(error)
                self.queue.put(
                    QueueMessage("error", self.task_name, message)
                )
                self.log.error(message)


class GitClient:
    """
    Class for cloning code and selecting specific versions from DCC-EX repositories
    """

    # Set up logger
    log = logging.getLogger(__name__)

    @staticmethod
    def get_repo(repo_dir):
        """
        Validate the provided directory is a repo

        Returns a tuple of (True|False, None|message)
        """
        git_file = os.path.join(repo_dir, ".git")
        try:
            repo = pygit2.Repository(git_file)
        except Exception:
            GitClient.log.error("%s not a repository", git_file)
            return False
        else:
            if isinstance(repo, pygit2.Repository):
                GitClient.log.debug(repo)
                return repo
            else:
                GitClient.log.error("%s not a repository", git_file)
                return False

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
                GitClient.log.error("Local file changes in %s", repo)
                GitClient.log.error(file_list)
            else:
                GitClient.log.debug("No local file changes in %s", repo)
        else:
            file_list = [f"{repo} is not a valid repository"]
            GitClient.log.error("%s not a valid repository", repo)
        return file_list

    @staticmethod
    def dir_is_git_repo(dir):
        """
        Check if directory exists and contains a .git file

        Returns True if so, False if not
        """
        git_file = os.path.join(dir, ".git")
        if os.path.exists(dir) and os.path.isdir(dir):
            if os.path.exists(git_file):
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def clone_repo(repo_url, repo_dir, queue):
        """
        Clone a remote repo using a separate thread

        Returns the repo instance in queue data if successful
        """
        task_name = "clone_repo"
        thread = ThreadedGitClient(task_name, pygit2.clone_repository, queue, repo_url, repo_dir)
        thread.start()

    @staticmethod
    def pull(repo, remote_name="origin", branch="master"):
        """
        Function to pull the latest updates from the provided repo

        Expects a pygit2 repo object and a branch name
        """
        for remote in repo.remotes:
            if remote.name == remote_name:
                remote.fetch()
                remote_master_id = repo.lookup_reference('refs/remotes/origin/%s' % (branch)).target
                merge_result, _ = repo.merge_analysis(remote_master_id)
                # Up to date, do nothing
                if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                    return True
                # We can just fastforward
                elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                    repo.checkout_tree(repo.get(remote_master_id))
                    try:
                        master_ref = repo.lookup_reference('refs/heads/%s' % (branch))
                        master_ref.set_target(remote_master_id)
                    except KeyError:
                        repo.create_branch(branch, repo.get(remote_master_id))
                    repo.head.set_target(remote_master_id)
                    return True
                else:
                    # raise AssertionError('Unknown merge analysis result')
                    return False

    @staticmethod
    def pull_latest(repo, branch, queue):
        """
        Pull latest updates from a repo

        Threaded version of pull

        Requires a pygit2 repo object and a branch name
        """
        task_name = "pull"
        thread = ThreadedGitClient(task_name, GitClient.pull, queue, repo, "origin", branch)
        thread.start()

    @staticmethod
    def get_branch_ref(repo, name):
        """
        Gets the ref for the named branch
        """
        branch = repo.lookup_branch(name)
        refname = repo.lookup_reference(branch.name)
        return refname

    @staticmethod
    def get_repo_versions(repo):
        """
        Gets all version tags from the specified repo

        Returns either an ordered dictionary (descending) or False if there are no tags
        """
        versions_unsorted = {}
        version_list = {}
        version_match = r"v(\d+)\.(\d+)\.(\d+)-(Prod|Devel)"
        refs = repo.references.iterator(2)
        for ref in refs:
            version = re.search(version_match, ref.shorthand)
            if version:
                numbers = {"major": int(version[1]),
                           "minor": int(version[2]),
                           "patch": int(version[3]),
                           "type": version[4],
                           "ref": ref.name}
                versions_unsorted[ref.shorthand] = numbers
                version_list = OrderedDict(sorted(versions_unsorted.items(),
                                           key=lambda t: (t[1]["major"],
                                                          t[1]["minor"],
                                                          t[1]["patch"]),
                                           reverse=True))
        return version_list

    @staticmethod
    def get_latest_prod(repo, tag_name="Prod"):
        """
        Retrieves the latest Production tagged version from the repo

        If no tags or no Prod tags, returns False
        """
        prod_version = None
        version_list = GitClient.get_repo_versions(repo)
        for version in version_list:
            if version_list[version]["type"] == "Prod":
                prod_version = (version, version_list[version]["ref"])
                break
        return prod_version

    @staticmethod
    def get_latest_devel(repo, tag_name="Devel"):
        """
        Retrieves the latest Development tagged version from the repo

        If no tags or no Devel tags, returns False
        """
        devel_version = None
        version_list = GitClient.get_repo_versions(repo)
        for version in version_list:
            if version_list[version]["type"] == "Devel":
                devel_version = (version, version_list[version]["ref"])
                break
        return devel_version
