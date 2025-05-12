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
from typing import Optional
import re

# Load environment variables from .env file
load_dotenv()

# Set GitHub token, name of the repository, and the current EX-Installer version
github_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("REPO")
current_version = ex_installer_version

# Connect to GitHub using the token and get the repository
github_instance = Github(github_token)
repo = github_instance.get_repo(repo_name)

def get_version_release(repo: Repository, version: str) -> Optional[GitRelease]:
    """
    Get the release for the provided version number.

    Args:
        repo (Repository): A GitHub repository instance
        version (str): String containing the current version number
    
    Returns:
        Optional[GitRelease]: Github release for this version, or None if it doesn't exist
    """
    version_release = None
    version_pattern = re.compile(rf"v?{re.escape(version)}(-\w+)?$")
    try:
        for release in repo.get_releases():
            if version_pattern.match(release.tag_name):
                version_release = release
                break
    except Exception as error:
        print(f"Could not check releases: {error}")
    return version_release

def get_version_tag(repo: Repository, version: str) -> Optional[str]:
    """
    Get the tag for the provided version number if it exists.

    Args:
        repo (Repository): A GitHub repository instance
        version (str): String containing the current version number
    
    Returns:
        Optional[str]: The tag if it exists, otherwise None
    """
    version_tag = None
    version_pattern = re.compile(rf"v?{re.escape(version)}(-\w+)?$")
    try:
        for tag in repo.get_tags():
            if version_pattern.match(tag.name):
                version_tag = tag.name
                break
    except Exception as error:
        print(f"Could not check tags: {error}")
    return version_tag

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

def create_draft_release(repo: Repository, version: str, production: bool) -> GitRelease:
    """
    Create a new draft release for the provided version.

    Args:
        repo (Repository): Instance of a repository to create the release for
        version (str): Version string to use for the release
        production (bool): Flag if this is a Production release or not
    
    Returns:
        GitRelease: An instance of a release
    """
    tag = get_version_tag(repo, current_version)
    if tag is None:
        try:
            tag = repo.create_git_tag(version, version, '', 'commit')
        except Exception as error:
            print(f"Error creating new tag: {error}")


release = get_version_release(repo, current_version)
if release:
    print(f"Release exists: {release.tag_name}")
else:
    create_draft_release(repo, current_version, False)



version_file_path = os.path.join(os.getcwd(), "ex_installer", "version.py")
notes = extract_release_notes(current_version, version_file_path)
print(notes)
