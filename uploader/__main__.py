import os
import shutil
import zipfile
import requests
from helpers import common
import paramiko
from tqdm import tqdm
import config as cfg


def upload_file(filepath_local: str, filename_remote: str):
    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            cfg.upload.host,
            cfg.upload.port,
            username=cfg.upload.username,
            password=cfg.upload.password,
        )

        sftp = ssh.open_sftp()
        sftp.chdir(cfg.upload.filepath)

        try:
            with tqdm(
                desc="Progress ", unit="iB", unit_scale=True, unit_divisor=1024
            ) as pbar:

                def progress(amt, tot):
                    pbar.total = tot
                    pbar.update(amt - pbar.n)

                sftp.put(filepath_local, filename_remote, callback=progress)

        finally:
            sftp.close()


def main():
    common.in_minecraft_folder()

    print(f"You are preparing to upload a new version of {cfg.pack.name}!" + os.linesep)

    common.continue_or_not()

    # Grab the version file data and save it here
    response = requests.get(cfg.pack.version)
    version_old = common.version_decode(response.text)

    while True:
        version_new = input(
            os.linesep
            + "Please enter a semantic version type to increase by 1 for this upload. (M)ajor, (m)inor (p)atch or a custom number with (c)ustom."
            + os.linesep
            + "> "
        )

        if version_new in ["M", "m", "p", "c"]:
            break
        elif version_new.lower() in ["major", "minor", "patch", "custom"]:
            version_new = version_new.lower()
            break
        else:
            print(
                f"{os.linesep}Please enter a valid option (full words or short-codes in backets. Short-codes are case-sensitive).{os.linesep}"
            )

    match version_new:
        case "M" | "major":
            version_old[0] += 1

        case "m" | "minor":
            version_old[1] += 1

        case "p" | "patch":
            version_old[2] += 1

        case "c" | "custom":
            while True:
                version_custom = input(
                    "Please enter your custom semantic version (e.g. 1.2.3):"
                    + os.linesep
                    + "> "
                )

                try:
                    version_old = common.version_decode(version_custom)
                    break
                except Exception as e:
                    print(os.linesep + e + os.linesep)

    version_new = common.version_encode(version_old[0], version_old[1], version_old[2])

    print(f"{os.linesep}Securing temporary directory...")
    common.rm_file_folder("upload_temp")

    print(f"{os.linesep}Creating temporary directory...")
    os.mkdir("upload_temp")

    print(f"{os.linesep}Updating server file with new version number...")
    f = open("upload_temp/version.txt", "w")
    f.write(f"{version_new}")
    f.close()
    print()
    upload_file("upload_temp/version.txt", "version.txt")

    print(f"{os.linesep}Zipping mods...")
    mods = common.list_items("../mods", include_folders=False)
    for file in tqdm(mods, desc="Progress "):
        zipfile.ZipFile("upload_temp/modpack.zip", mode="a").write(file)

    print(f"{os.linesep}Zipping configs...")
    configs = common.list_items("../config", include_folders=False)
    for file in tqdm(configs, desc="Progress "):
        zipfile.ZipFile("upload_temp/modpack.zip", mode="a").write(file)

    print(f"{os.linesep}Uploading pack with 'v{version_new}' tag...")
    upload_file("upload_temp/modpack.zip", f"modpack_v{version_new}.zip")

    print(f"{os.linesep}Uploading pack with 'latest' tag...")
    upload_file("upload_temp/modpack.zip", f"latest.zip")

    print(f"{os.linesep}Cleaning up temporary files...{os.linesep}")
    shutil.rmtree("upload_temp")

    return 0


if __name__ == "__main__":
    main()
