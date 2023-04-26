# Imports
import os
from tkinter import messagebox
import time
import shutil
from tqdm import tqdm
import config as cfg
from helpers import common
import sys
from tqdm import tqdm


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

    return


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
            sys.argv[0]
            .replace("\\modpack-update.exe", "")
            .replace("modpack-update", "")
        )

        os.chdir(script_dir)
    except:
        print(sys.argv)
        print("No args given! Please include the tools dir abs path as an arg.")
        common.conMessagetinue_or_not("")
        return

    # MC folder check
    common.in_minecraft_folder()

    # Check for newer version of updater
    if cfg.updater.check_version:
        updater_outdated = common.version_behind(
            "version.txt", cfg.updater.version, "updater"
        )
        if updater_outdated:
            # Download the update
            print(f"{os.linesep}Grabbing new update...")
            file_name = common.download(
                cfg.updater.temp_dir, cfg.updater.url, "updater"
            )

            # Unpack the update
            print(f"{os.linesep}Unpacking update...")
            unpacked = common.unzip(
                cfg.updater.temp_dir, f"{cfg.updater.temp_dir}/updater.zip"
            )

            # Finish up message so people arent concerned with the crash
            messagebox.showwarning(
                title="Modpack Updater",
                message="Update ready to restore files! When finished, the process will crash, then you can launch your instance as normal!",
            )

            # Restore new files
            print(f"{os.linesep}Copying update files...")
            common.copy_progress(unpacked, "./")
            return

    pack_outdated = common.version_behind("../version.txt", cfg.pack.version, "modpack")

    if pack_outdated:
        version_remote = pack_outdated
        print(f"{os.linesep}Downloading the latest version of the pack...{os.linesep}")

        # Get remote zip
        common.download("update_temp", cfg.pack.url, "modpack")

        # Unzip mods
        print(f"{os.linesep}Unpacking update zip...{os.linesep}")
        unpacked = common.unzip(cfg.updater.temp_dir, "update_temp/modpack.zip")

        # Sync all downloaded files
        print(f"{os.linesep}Matching local with remote data...{os.linesep}")
        src_mods = f"{unpacked}/mods"
        print(f"{os.linesep}Mods: ")
        update_apply(src_mods, "../mods")

        # Clean up the temp folder(s)
        print(f"{os.linesep}Cleaning up temporary files...{os.linesep}")
        shutil.rmtree(cfg.updater.temp_dir)

        # Update local version number to match remote
        print(f"{os.linesep}Updating local version number...{os.linesep}")
        with open("../version.txt", "w") as f:
            f.write(
                common.version_encode(
                    version_remote[0],
                    version_remote[1],
                    version_remote[2],
                )
            )

        # Finish up!
        print("Update completed successfully!")

    print("Launching instance...")
    time.sleep(1)
    return

    # # Make ./update_temp/unpacked if it doesnt exist
    # if not os.path.isdir("update_temp/unpacked"):
    #     os.mkdir("update_temp/unpacked")

    # # Unpack zip to ./update_temp/unpacked
    # with zipfile.ZipFile("update_temp/modpack.zip") as zf:
    #     for member in tqdm(zf.infolist(), desc="Progress "):
    #         try:
    #             zf.extract(member, "update_temp/unpacked")

    #         except zipfile.error as e:
    #             pass

    # src_config = "update_temp/unpacked/config"

    # Update confifg files
    # print("Configs: ")
    # update_apply(src_config, "../config")


if __name__ == "__main__":
    main()
