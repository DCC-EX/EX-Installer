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
from github.InputGitAuthor import InputGitAuthor
import os
from dotenv import load_dotenv
from ex_installer.version import ex_installer_version
from typing import Optional, List
import re
import argparse
import traceback

# Script brief
SCRIPT_BRIEF = """\
============================
EX-Installer Release Manager
============================

This script automates the release management process for EX-Installer and takes care of:

- Creating the required GitHub tag
- Creating the required GitHub release
- Uploading the required distribution files to the release
- Publishing the release
"""

# Script notes
SCRIPT_NOTES = """\
To run this script, you must copy the provided '.env.example' file to '.env' and update it.

It must contain a valid GitHub personal access token with these privileges on the DCC-EX/EX-Installer repository:

- Contents - read/write
- Deployments - read/write
- Metadata - read

When running this script, you must specify at least one of:

- -F|--files: A comma separated list of files to upload, which must be located in your local EX-Installer/dist folder
- -D|--delete: A file to be deleted from the release
- -P|--publish: If specified, the release will be published, otherwise it will be created as a draft

Note: You cannot specify both -F|--files and -D|--delete at the same time.

To publish an EX-Installer release, three distribution files are expected to be attached as assets:

- EX-Installer-Linux64 - 64bit Linux binary
- EX-Installer-macOS - macOS binary
- EX-Installer-Setup-Win64.exe - Windows 64bit installer executable built by Inno Setup

When publishing, if any of these are not present, a warning will be generated, with a prompt to continue or cancel.
"""

# Create argument parser and add arguments
parser = argparse.ArgumentParser(
    description=SCRIPT_BRIEF,
    epilog=SCRIPT_NOTES,
    formatter_class=argparse.RawTextHelpFormatter
)

# Add branch and publish arguments
parser.add_argument("-B", "--branch", help="Branch to use the latest commit from for tagging",
                    required=True, dest="branch")
parser.add_argument(
    "-P", "--publish", help="If provided, this will trigger the release to be published rather than remaining a draft",
    action="store_true")
# Add files and delete group arguments, either must be specified, but not both
file_arg_group = parser.add_mutually_exclusive_group()
file_arg_group.add_argument(
    "-F", "--files", help="Comma separated list of files in the 'dist' folder to attach to the release", dest="files")
file_arg_group.add_argument(
    "-D", "--delete", help="Single file to be deleted from the release, cannot use with -F|--files", dest="delete")

# Parse the args ready for validation later
args = parser.parse_args()

# Validate args before proceeding
if not args.files and not args.delete and not args.publish:
    parser.error("You must specify at least one of -F|--files, -D|--delete, -P--publish.")

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


def create_draft_release(repo: Repository,
                         tag_name: str,
                         author: InputGitAuthor,
                         release_notes: str) -> Optional[GitRelease]:
    """
    Create a new draft release for the provided version.

    Args:
        repo (Repository): Instance of a repository to create the release for
        tag_name (str): Tag name to associate with this release
        author (InputGitAuthor): Instance of an author for the tag/release
        release_notes (str): Release notes to include in this release

    Returns:
        Optional[GitRelease]: An instance of a release or None if creation fails
    """
    # First make sure we have a tag associated with the latest commit
    git_tag = None
    release = None
    release_name = "EX-Installer Release " + tag_name
    for tag in repo.get_tags():
        if tag.name == tag_name:
            git_tag = tag
            break
    # If no tag, create release and tag based on latest commit
    if git_tag is None:
        # Get the latest commit
        print("Creating a new tag...")
        commit_sha = repo.get_commits()[0].sha
        try:
            git_tag = repo.create_git_tag(
                tag=tag_name,
                message=tag_name,
                object=commit_sha,
                type='commit',
                tagger=author
            )
        except Exception as error:
            print(f"ERROR: Could not create tag: {repr(error)}")
            print("Traceback:")
            traceback.print_exc()
    if git_tag:
        try:
            release = repo.create_git_release(
                tag=tag_name,
                name=release_name,
                message=release_notes,
                draft=True,
                prerelease=False,
                generate_release_notes=False,
                make_latest="false"
            )
        except Exception as error:
            print(f"ERROR: Could not create release: {repr(error)}")
            print("Traceback:")
            traceback.print_exc()
    return release


def check_missing_assets(release: GitRelease) -> List:
    """
    Check if this release is missing required assets:
        - EX-Installer-Linux64
        - EX-Installer-macOS
        - EX-Installer-Setup-Win64.exe

    Args:
        release (GitRelease): Instance of the release to validate assets for

    Returns:
        List: List of missing assets, empty if all are present
    """
    asset_list = ['EX-Installer-Linux64', 'EX-Installer-macOS', 'EX-Installer-Setup-Win64.exe']
    for asset in release.get_assets():
        if asset.name in asset_list:
            asset_list.remove(asset.name)

    return asset_list


def publish_release(repo: Repository, release: GitRelease):
    """
    Publish the specified release.

    If this is a production release, it will be made the latest also.

    If this is a development release and there are no other production releases, it will be made the latest.

    Args:
        repo (Repository): The repository this release is associated with
        release (GitRelease): Instance of the release to publish
    """
    name = release.title
    message = release.body
    make_latest = "false"
    if "-Prod" in release.tag_name:
        make_latest = "true"
    else:
        # If there are no production releases and this is devel, it should still be the latest
        prod = any("-Prod" in rel.tag_name for rel in repo.get_releases())
        if not prod:
            make_latest = "true"

    try:
        release.update_release(name=name, message=message, draft=False, make_latest=make_latest)
    except Exception as error:
        print(f"ERROR: Could not publish release: {repr(error)}")
        print("Traceback:")
        traceback.print_exc()


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


def valid_email(email: str) -> bool:
    """
    Validate that the provided email address is formatted correctly.

    Args:
        email (str): Email address to check

    Returns:
        bool: True if valid, False if not
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def get_author(github_instance: Github) -> InputGitAuthor:
    """
    Get the author for creating tags/releases.

    Args:
        github_instance (Github): Instance of a GitHub connection to get the current user from

    Returns:
        InputGitAuthor: Instance of an author to associate with a tag and release
    """
    github_user = github_instance.get_user()
    user_name = None
    user_email = None
    if github_user.name and github_user.email:
        user_name = github_user.name
        user_email = github_user.email
    else:
        commits = repo.get_commits(author=github_user.login)
        if commits.totalCount > 0:
            user_name = github_user.name
            user_email = commits[0].commit.author.email
        else:
            while True:
                user_email = input("Could not determine your email address for the release, enter it here: ")
                if valid_email(user_email):
                    user_name = github_user.name
                    break
                else:
                    print("Invalid email address provided, try again.")

    # Create the InputGitAuthor instance to author tags/releases
    return InputGitAuthor(name=user_name, email=user_email)


def add_file_to_release(release: GitRelease, file_path: str):
    """
    Add the specified file to the specified release as an asset.

    Args:
        release (GitRelease): Instance of the release to add the file too
        file_path (str): Full path to the file to add
    """
    if not os.path.isfile(file_path):
        print(f"Provided path is not a file: {file_path}")
        return
    for asset in release.get_assets():
        if asset.name in file_path:
            print("WARNING: File exists already, deleting before uploading.")
            delete_file_from_release(release, asset.name)
    try:
        release.upload_asset(
            path=file_path,
            label=''
        )
    except Exception as error:
        print(f"Could not add {file_path} to release: {repr(error)}")
        print("Traceback:")
        traceback.print_exc()


def delete_file_from_release(release: GitRelease, file_name: str):
    """
    Delete the asset associated with the specified file name from the specified release.

    Args:
        release (GitRelease): Instance of the release to delete the file from
        file_name (str): Name of the file to delete
    """
    file_exists = False
    for asset in release.get_assets():
        if asset.name == file_name:
            file_exists = True
            try:
                asset.delete_asset()
            except Exception as error:
                print(f"Could not delete file {file_name} from release: {repr(error)}")
                print("Traceback:")
                traceback.print_exc()
    if not file_exists:
        print(f"WARNING: File {file_name} is not an asset of this release, skipping.")


def validate_inno_setup_version(version: str, inno_setup_path: str) -> bool:
    """
    Validates that the version in 'ex-installer.iss' matches the EX-Installer version.

    Args:
        version (str): EX-Installer version to match
        inno_setup_path(str): Path to the ex-installer.iss file

    Returns:
        bool: True if version matches, otherwise False
    """
    if os.path.isfile(inno_setup_path):
        with open(inno_setup_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith('#define MyAppVersion'):
                    match = re.search(r'#define MyAppVersion\s*"(.+)".*$', line)
            if match:
                iss_version = match.group(1)
                if iss_version == version:
                    return True
                else:
                    print(f"ERROR: Expected Inno Setup version {version}, found {iss_version}")
                    return False
    else:
        print(f"ERROR: {inno_setup_path} is not a valid file")
        return False
    return False


"""
This script will use the version in version.py to determine the release type and tag name:
- Anything less than 1.x.x is development (vX.Y.Z-Devel)
- Once reaching 1.Y.Z, like EX-CommandStation, odd Y = Devel, even Y = Prod

Script must validate that the version in version.py matches the version in ex-installer.iss.

Mandatory user arguments to provide:
- Current working branch - need to use this for the correct commit SHA for the version tag
- Binary/.exe to add as an asset to the release
- Publish the release (optional)
"""
# Connect to GitHub using the token and get the repository
try:
    print("Connecting to GitHub...")
    github_instance = Github(github_token)
except Exception as error:
    print(f"Could not connect to GitHub: {error}")
    exit()

# Validate the provided repository exists, and get it
try:
    print(f"Getting repository {repo_name}...")
    repo = github_instance.get_repo(repo_name)
except Exception as error:
    print(f"Could not get repository '{repo_name}': {error}")
    exit()

# Get the author for the release
print("Getting release author...")
author = get_author(github_instance)

# If files are to be added, validate and build the file path list
if args.files:
    print("Validating file list to add...")
    file_list = process_file_list(args.files)
    if len(file_list) == 0:
        print("ERROR: You haven't provided any valid files, at least one file must be provided.")
        exit()

# Validate Inno Setup version is set correctly
print("Validating Inno Setup version matches EX-Installer version...")
inno_setup_file = os.path.join(os.getcwd(), "InnoSetup", "ex-installer.iss")
inno_setup_valid = validate_inno_setup_version(ex_installer_version, inno_setup_file)
if inno_setup_valid is False:
    print("ERROR: Inno Setup version mismatch, aborting.")
    exit()

# Get the tag name that should be associated with this release
tag_name = build_tag_name(ex_installer_version)
if tag_name is None:
    print(f"Could not create tag name from '{ex_installer_version}', aborting.")
    exit()
else:
    print(f"Using tag name {tag_name} for release")

# Now check if we have a release
print("Checking for an existing release...")
release = get_version_release(repo, tag_name)
if release is None:
    print("No existing release found, creating a new one...")
    version_file_path = os.path.join(os.getcwd(), "ex_installer", "version.py")
    release_notes = extract_release_notes(ex_installer_version, version_file_path)
    release = create_draft_release(repo, tag_name, author, release_notes)

# If release was not found and couldn't be created, we can't continue
if release is None:
    print("ERROR: No release exists and creation has failed, aborting.")
    exit()

# If adding files, do so now
if args.files:
    print("Adding files to release...")
    for file_path in file_list:
        print(f"Adding file {file_path}...")
        add_file_to_release(release, file_path)

# If deleting a file, do so now
if args.delete:
    print(f"Deleting file {args.delete} from release...")
    delete_file_from_release(release, args.delete)

# If publishing, do it
if args.publish:
    # Make sure all required assets are present before publishing
    missing_assets = check_missing_assets(release)
    if len(missing_assets) > 0:
        print("WARNING: The following files are missing from this release:")
        for file in missing_assets:
            print(file)
        # If assets are missing, prompt to publish or not
        while True:
            confirm = input("Do you wish to publish anyway? (Y/N): ").strip().lower()
            if confirm == 'y':
                break
            elif confirm == 'n':
                print("Aborting.")
                exit()
            else:
                print("Invalid response, enter Y|y or N|n.")
    print("Publishing release...")
    publish_release(repo, release)
