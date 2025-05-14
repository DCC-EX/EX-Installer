"""
Python script to manage EX-Installer GitHub releases.

© 2025, Peter Cole. All rights reserved.

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
from github import Github
from github.Repository import Repository
from github.GitRelease import GitRelease
import os
from dotenv import load_dotenv
from ex_installer.version import ex_installer_version
from typing import Optional, List
import re
import argparse

# Create argument parser and add arguments
parser = argparse.ArgumentParser()

# Add branch and publish arguments
parser.add_argument("-B", "--branch", help="Branch to use the latest commit from for tagging",
                    required=True, dest="branch")
parser.add_argument(
    "-P", "--publish", help="If provided, this will trigger the release to be published rather than remaining a draft",
    action="store_true")
# Add files and delete group arguments, either must be specified, but not both
file_arg_group = parser.add_mutually_exclusive_group(required=True)
file_arg_group.add_argument(
    "-F", "--files", help="Comma separated list of files in the 'dist' folder to attach to the release", dest="files")
file_arg_group.add_argument(
    "-D", "--delete", help="Single file to be deleted from the release, cannot use with -F|--files", dest="delete")

# Parse the args ready for validation later
args = parser.parse_args()

# Load environment variables from .env file
load_dotenv()

# Set GitHub token, name of the repository, and the current EX-Installer version
github_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("REPO")


"""
All functions for this script are below, script logic follows these.
"""


def get_version_release(repo: Repository, tag_name: str) -> Optional[GitRelease]:
    """
    Get the release for the provided tag name.

    Args:
        repo (Repository): A GitHub repository instance
        tag_name (str): String containing the tag this release should be associated with

    Returns:
        Optional[GitRelease]: Github release for this version, or None if it doesn't exist
    """
    version_release = None
    try:
        for release in repo.get_releases():
            if release.tag_name == tag_name:
                version_release = release
                break
    except Exception as error:
        print(f"Could not check releases: {error}")
    return version_release


def extract_release_notes(version: str, file_path: str) -> str:
    """
    Extract release notes from version.py for the provided version.

    Args:
        version (str): String containing the current version number
        file_path (str): Path to version.py

    Returns:
        str: Release notes in markdown format
    """
    notes = []
    capture = False
    version_start_pattern = re.compile(rf"^{version}\b")
    version_stop_pattern = re.compile(r"^\d+\.\d+\.\d+")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if version_start_pattern.match(line):
                    capture = True
                    text_only = re.sub(rf"^{version}\s*-", "-", line)
                    notes.append(text_only)
                elif capture and version_stop_pattern.match(line):
                    break
                elif capture and line:
                    notes.append(f"{line}")
    except Exception as error:
        print(f"Could not get contents from {file_path}: {error}")
    return "\n".join(f"{note}" for note in notes)


def create_draft_release(repo: Repository, tag_name: str, author: str, release_notes: str, publish: bool) -> GitRelease:
    """
    Create a new draft release for the provided version.

    Args:
        repo (Repository): Instance of a repository to create the release for
        tag_name (str): Tag name to associate with this release
        author (str): Author of the tag/release
        release_notes (str): Release notes to include in this release
        publish (bool): Flag if this should be published or just a draft

    Returns:
        GitRelease: An instance of a release
    """
    # First make sure we have a tag associated with the latest commit
    git_tag = None
    release = None
    release_name = "EX-Installer Release " + tag_name
    if publish:
        draft = False
    else:
        draft = True
    for tag in repo.get_tags():
        if tag.name == tag_name:
            git_tag = tag
            break
    # If no tag, create release and tag based on latest commit
    if git_tag is None:
        # Get the latest commit
        commit_sha = repo.get_commits()[0].sha
        print(f"Using commit with SHA {commit_sha}")
        try:
            release = repo.create_git_tag_and_release(
                tag_name, tag_name, release_name, release_notes,
                commit_sha, 'commit', author, draft, False, False, publish)
        except Exception as error:
            print(f"ERROR: Could not create tag or release: {error}")
    else:
        try:
            release = repo.create_git_release(tag_name, release_name, release_notes, draft, False, False, '', publish)
        except Exception as error:
            print(f"Could not create release: {error}")
    return release


def process_file_list(files: str) -> List:
    """
    Processes a comma separated list of files into a List of full file paths.

    Args:
        files (str): String containing comma separated list of files

    Returns:
        List: List of file paths
    """
    file_paths = []
    for file_name in files.split(","):
        file_path = os.path.join(os.getcwd(), "dist", file_name.strip())
        if os.path.isfile(file_path):
            file_paths.append(file_path)
        else:
            print(f"WARNING: Provided file '{file_path}' is not a valid file and will not be added to the release.")
    return file_paths


def build_tag_name(version: str) -> Optional[str]:
    """
    Use the provided version string to determine the correct Git tag for the release.

    Any version less than 1.y.z will be Devel.
    Any version after 1.y.z with even y will be Prod.
    Any version after 1.y.z with odd y will be Devel.

    Args:
        version (str): Semantic version string in 'X.Y.Z' format

    Returns:
        Optional (str): Tag name string in 'vX.Y.Z-[Devel|Prod]' format, or None if version is not valid
    """
    production = False
    version_numbers = []
    # If we don't have exactly 3, invalid
    if len(version.split('.')) != 3:
        return None
    # Validate each item is a digit
    for number in version.split('.'):
        number = number.strip()
        if not number.isdigit():
            return None
        version_numbers.append(int(number))
    # 1.y.z or later and y is even = production
    if version_numbers[0] > 0 and version_numbers[1] % 2 == 0:
        production = True
    # If we got here, build our tag
    version_tag = "v" + ".".join(map(str, version_numbers))
    if production:
        version_tag += "-Prod"
    else:
        version_tag += "-Devel"
    return version_tag


"""
This script will use the version in version.py to determine the release type and tag name:
- Anything less than 1.x.x is development (vX.Y.Z-Devel)
- Once reaching 1.Y.Z, like EX-CommandStation, odd Y = Devel, even Y = Prod

Script must validate that the version in version.py matches the version in ex-installer.iss.

Mandatory user arguments to provide:
- Current working branch - need to use this for the correct commit SHA for the version tag
- Binary/.exe to add as an asset to the release
- Publish the release (optional)

Process:
- Validate arguments are valid (Branch must exist, files must exist, cannot add and delete)
- Check if a release exists for the current version (get_version_release())
- If not, check if a tag exists (get_version_tag())
- If not, get latest commit SHA and create new tag
- Extract release notes from version.py (extract_release_notes())
- Create new draft release with tag and release notes using version as name (create_draft_release())
- Add the provided binary/.exe to the asset
- If release exists, just add asset
- If publish flag set, set as the latest release and publish

Optional:
- Remove or update an asset
"""
# Connect to GitHub using the token and get the repository
try:
    github_instance = Github(github_token)
except Exception as error:
    print(f"Could not connect to GitHub: {error}")
    exit()

# Validate the provided repository exists, and get it
try:
    repo = github_instance.get_repo(repo_name)
except Exception as error:
    print(f"Could not get repository '{repo_name}': {error}")
    exit()

# Get the author name for creating tags/releases
author = github_instance.get_user().login

# If files are to be added, validate and build the file path list
file_list = process_file_list(args.files)
if len(file_list) == 0:
    print("ERROR: You haven't provided any valid files, at least one file must be provided.")
    exit()

# Get the tag name that should be associated with this release
tag_name = build_tag_name(ex_installer_version)
if tag_name is None:
    print(f"Could not create tag name from '{ex_installer_version}', aborting.")
    exit()

# Now check if we have a release
release = get_version_release(repo, tag_name)
if release:
    print(f"Release exists: {release.tag_name}")
else:
    version_file_path = os.path.join(os.getcwd(), "ex_installer", "version.py")
    release_notes = extract_release_notes(ex_installer_version, version_file_path)
    create_draft_release(repo, tag_name, author, release_notes, args.publish)
