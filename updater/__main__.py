# Imports
import os
import time
import requests
import shutil
import zipfile
from tqdm import tqdm
import config as cfg
from helpers import common
import sys


# Downloads assets from your packs host
def update_download(url):
    # Make a ./update_temp directory if it doesnt exist
    if not os.path.isdir("update_temp"):
        os.mkdir("update_temp")

    # Make an HTTP request within a context manager
    with requests.get(url, stream=True) as r:
        # Check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))

        # Implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="Progress ") as raw:
            # Save the output to a file
            with open("update_temp/modpack.zip", "wb") as output:
                shutil.copyfileobj(raw, output)


def update_apply(src_dir, dst_dir):
    items = common.list_items(dst_dir)

    # Wipes / recreates all files / folders in relevant directories
    for file in tqdm(items, desc="Deleting files "):
        if os.path.isfile(file):
            os.remove(file)
        else:
            os.rmdir(file)

    print(f"Re-creating directory...")
    os.mkdir(dst_dir)

    common.copy_progress(src_dir, dst_dir)

    return 0


def main():
    # Welcome message
    print(
        f"# ---------------------------------------------- #{os.linesep}"
        + f"#                 Modpack Update                 #{os.linesep}"
        + f"# ---------------------------------------------- #{os.linesep}"
        + os.linesep
        + f"Thank you for choosing {cfg.pack.name}!{os.linesep}"
    )

    try:
        script_dir = (
            sys.argv[0].replace("modpack-update", "").replace("modpack-update.exe", "")
        )

        os.chdir(script_dir)
    except:
        print(sys.argv)
        print("No args given! Please include the tools dir abs path as an arg.")
        common.continue_or_not("")
        return

    # MC folder check
    common.in_minecraft_folder()

    # Run version check by comparing local version txt to remote version contents
    print(f"{os.linesep}Checking for version discrepency...")
    file_rversion = open("../version.txt", "r+")
    version_local = common.version_decode(file_rversion.readline())
    version_remote = common.version_decode(requests.get(cfg.pack.version).text)
    outdated = False

    for i in range(0, 3):
        if version_local[i] < version_remote[i]:
            outdated = True

    if not outdated:
        print("No updates found! Launching instance...")
        time.sleep(1)
        return

    print(f"{os.linesep}Downloading the latest version of the pack...{os.linesep}")

    # Get remote zip
    update_download(cfg.pack.url)

    print(f"{os.linesep}Unpacking update zip...{os.linesep}")

    # Make ./update_temp/unpacked if it doesnt exist
    if not os.path.isdir("update_temp/unpacked"):
        os.mkdir("update_temp/unpacked")

    # Unpack zip to ./update_temp/unpacked
    with zipfile.ZipFile("update_temp/modpack.zip") as zf:
        for member in tqdm(zf.infolist(), desc="Progress "):
            try:
                zf.extract(member, "update_temp/unpacked")

            except zipfile.error as e:
                pass

    print(f"{os.linesep}Matching local with remote data...{os.linesep}")

    src_config = "update_temp/unpacked/config"
    src_mods = "update_temp/unpacked/mods"

    # Update confifg files
    print("Configs: ")
    update_apply(src_config, "../config")

    print()

    # Update mod files
    print("Mods: ")
    update_apply(src_mods, "../mods")

    # Clean up the update_temp folder
    print(f"{os.linesep}Cleaning up temporary files...{os.linesep}")
    shutil.rmtree("./update_temp")

    # Update local version number to match remote
    print(f"{os.linesep}Updating local version number...{os.linesep}")
    file_rversion.write(
        common.version_encode(version_remote[0], version_remote[1], version_remote[2])
    )
    file_rversion.close()

    # Finish up!
    print("Update completed successfully! Launching instance...")
    time.sleep(1)

    return


if __name__ == "__main__":
    main()
