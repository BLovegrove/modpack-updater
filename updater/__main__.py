# Imports
import os
import requests
import shutil
import zipfile
from tqdm import tqdm
import config as cfg
from helpers import common


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
    # MC folder check
    common.in_minecraft_folder()

    # Welcome message
    print(
        f"Thank you for choosing {cfg.pack.name}!"
        + (os.linesep * 2)
        + f"Please make sure you have this program in your packs Minecraft folder "
        + "with a shortcut to it placed somewhere else before continuing."
        + os.linesep
        + "(If this is a fresh install - you probably don't have to worry about this.)"
        + os.linesep
    )

    # User confirmation dialogue
    common.continue_or_not()

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

    # Finish up!
    print(
        "Done! You can now launch the pack. If you experience any technical difficulties let your friendly neighbrhood server admin know ASAP!"
    )

    # User confirmation dialogue
    common.continue_or_not("")

    return 0


if __name__ == "__main__":
    main()
