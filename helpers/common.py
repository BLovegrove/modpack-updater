import os
import re
import shutil
import sys
import zipfile
import requests
from tqdm import tqdm
from urllib.parse import urlparse


# Deletes target regardless of file or folder status
def rm_file_folder(target):
    if os.path.isfile(target):
        os.remove(target)

    elif os.path.isdir(target):
        # rmtree remves diirectory ad *all* contents
        shutil.rmtree(target)

    else:
        # Safely continues if nothing was found instead of throwing an error
        pass

    return 0


# Generate list of all files / folders in target directory and orders them items -> folders(reverse order) intended for deletion
def list_items(target_dir: str, include_folders: bool = True):
    files = []
    folders = []

    # Walks through dir getting filenames and foldernames seperately
    for root, subfolder, filenames in os.walk(target_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))

        if include_folders:
            folders.append(root)

    # Flips order of folders to avoid 'not empty' error.
    folders.reverse()

    # Assembles both lists into one, deleting files first and folders last
    items = files + folders

    return items


# Scans for the folders the program needs to run. Kills the program if nothing is found.
def in_minecraft_folder():
    if os.path.isdir("../config") and os.path.isdir("../mods"):
        return

    else:
        print(
            "Minecraft folder not detected! Make sure you put the program folder in your Minecraft folder."
        )
        continue_or_not("")
        sys.exit(0)


def download(dl_dir: str, url: str, name: str = None):
    """Downloads a given file

    Args:
        dl_dir (str): local directory to place the fownloaded file (Will create one if it doesnt exist)
        url (str): remote location to pull the file from
        name (str, optional): local filename to replace default (excl. extension)

    Returns:
        str: basename of the file you downloaded
    """
    # Ensure download dir exists, create it if not
    if not os.path.isdir(dl_dir):
        os.makedirs(dl_dir)

    # Make an HTTP request within a context manager
    with requests.get(url, stream=True) as r:
        # Check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        f_base = os.path.basename(urlparse(url).path).split(".")
        f_name = f_base[0]
        f_ext = f_base[1]

        # Implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="Progress ") as raw:
            # Save the output to a file
            with open(
                f"{dl_dir}/{f_name if not name else name}.{f_ext}", "wb"
            ) as output:
                shutil.copyfileobj(raw, output)

    return f"{f_name}.{f_ext}"


def unzip(unpack_dir: str, f_path: str):
    """Unzips a standard ZIP file to a specified directory

    Args:
        unpack_dir (str): directory to unpack your files to
        f_path (str): path to the ZIP file you wish to unpack

    Returns:
        str: path to the folder the zip was unpacked into
    """
    f_name = f_path.split("/")[-1].split(".")[0]

    # Make unpack folder if it doesnt exist (same name as zip being unpacked)
    if not os.path.isdir(f"{unpack_dir}/{f_name}"):
        os.mkdir(f"{unpack_dir}/{f_name}")

    # Unpack zip
    with zipfile.ZipFile(f_path) as zf:
        for member in tqdm(zf.infolist(), desc="Progress "):
            try:
                zf.extract(member, f"{unpack_dir}/{f_name}")

            except zipfile.error as e:
                pass

    return f"{unpack_dir}/{f_name}"


# Checks if local version is behind remote version,
def version_behind(local_version_file: str, remote_version_file: str, subject: str):
    print(f"{os.linesep}Checking for latest {subject} version...")
    with open(local_version_file, "r") as f:
        version_local = version_decode(f.readline())
    version_remote = version_decode(requests.get(remote_version_file).text)
    outdated = False

    # Run version check by comparing local version txt to remote version contents
    for i in range(0, 3):
        if version_local[i] < version_remote[i]:
            outdated = True

    if outdated:
        return version_remote
    else:
        return


# prompts user for some input to continue or quit
def continue_or_not(input_message: str = "Would you like to continue?"):
    while True:
        reply: str = input(
            f"{input_message} Enter (y)es to confirm or anything else to cancel: {os.linesep}> "
        )

        if reply.lower() == "y" or reply.lower() == "yes":
            break

        else:
            sys.exit(0)

    return 0


# Copies files / folders from one dir to another with progress bar
def copy_progress(src_dir, dst_dir):
    for item in tqdm(os.listdir(src_dir), desc="Progress "):
        item_abs = os.path.join(src_dir, item)

        if os.path.isfile(item_abs):
            shutil.copy2(item_abs, dst_dir)
        else:
            shutil.copytree(item_abs, dst_dir + f"/{item}", dirs_exist_ok=True)


# Converts 3 integers into a valid semantic version string
def version_encode(major_version: int, minor_version: int, patch_version: int):
    return f"{major_version}.{minor_version}.{patch_version}"


# Converts a valid semantic version string into a list of 3 integers
def version_decode(version: str):
    semantic_exception = "Semantic Format Error: Semantic version must contain 3 integers seperated by 3 period characters. E.g. '1.0.32'"

    version_numbers = version.split(".")
    version_numbers = [int(i) for i in version_numbers]

    if len(version_numbers) != 3:
        raise Exception(semantic_exception)

    else:
        return version_numbers
