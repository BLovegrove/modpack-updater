import sys
from packaging import version
import os
import pathlib
from urllib.parse import urlsplit
from tkinter import messagebox
import requests
import toml
from tqdm import tqdm
import config as cfg


def main():
    # check for dry run arg -------------------------------------------------------------------------- #
    if "-d" in sys.argv or "--dryrun" in sys.argv:
        dry_run = True
        print("! == THIS IS A DRY RUN == !")
    else:
        dry_run = False

    os.chdir(os.path.dirname(sys.argv[0]))

    # welcome message -------------------------------------------------------------------------------- #
    print(
        f"# ---------------------------------------------- #{os.linesep}"
        + f"#                 Modpack Update                 #{os.linesep}"
        + f"# ---------------------------------------------- #{os.linesep}"
        + os.linesep
        + f"Thank you for choosing {cfg.pack.name}!{os.linesep*2}"
    )

    # check client can see server -------------------------------------------------------------------- #
    split_url = urlsplit(cfg.pack.url)
    try:
        response = int(
            requests.get(f"{split_url.scheme}://{split_url.netloc}").status_code
        )

        if response == 200:
            con_status = True
        else:
            con_status = False

    except requests.exceptions.ConnectionError:
        con_status = False

    if con_status == False:
        message = (
            "FAILED TO CONNECT TO MODPACK HOST SERVER."
            + os.linesep * 2
            + "Please check your internet connection or talk to your pack host if you want the most recent update."
        )

        messagebox.showerror(title="ERROR", message=message)

        return

    else:
        print("Connection status: Good")

    print(os.linesep)

    # check current version against most recent remote version --------------------------------------- #
    changelog = toml.loads(
        requests.get(cfg.pack.url + "/changelog.toml", stream=True).content.decode()
    )

    if not os.path.exists("../version.txt"):
        print("Version file not found - creating file with version 0.0.0...")
        pathlib.Path("../version.txt").write_text("0.0.0", encoding="utf-8")

    current_version = pathlib.Path("../version.txt").read_text()
    update_queue: list[dict[str, any]] = []

    for update in changelog["updates"]:
        if version.parse(update["version"]) > version.parse(current_version):
            update_queue.append(update)

    if len(update_queue) <= 0:
        print("Modpack up to date! Your instance should launch shortly...")
        return

    print(os.linesep)

    # process updates into single process queue ------------------------------------------------------ #
    print("Update detected! Collating changes since last update...")

    process_queue: dict[str, list[str]] = {"download": [], "remove": []}

    for update in update_queue:
        print(f"Compiling changes from v{update['version']}...")

        for key in update.keys():
            if key == "version" or key == "timestamp":
                continue
            try:
                for item in update[key]["add"]:
                    if item not in process_queue["download"]:
                        process_queue["download"].append(item)
            except KeyError as e:
                pass

            try:
                for item in update[key]["rem"]:
                    if item not in process_queue["remove"]:
                        process_queue["remove"].append(item)
            except KeyError as e:
                pass

    print(os.linesep)

    # execute process queue downloading and deleting files where needed ------------------------------ #
    print("Executing changes...")
    if len(process_queue["download"]) > 0:
        for file in tqdm(
            process_queue["download"], "Downloading", leave=True, position=0
        ):
            filepath = "../" + file
            if not dry_run:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                if os.path.exists(filepath):
                    os.remove(filepath)

                with open(filepath, "wb") as f:
                    f.write(requests.get(f"{cfg.pack.url}/{file}").content)

    if len(process_queue["remove"]) > 0:
        for file in tqdm(process_queue["remove"], "Deleting", leave=True, position=0):
            filepath = "../" + file
            if not dry_run:
                try:
                    os.remove(filepath)
                except FileNotFoundError as e:
                    print(f"File not found. Can't remove.")

    print(os.linesep)

    # change local version to match remote ----------------------------------------------------------- #
    print("Updating version file...")
    with open("../version.txt", "w") as f:
        f.write(update_queue[0]["version"])

    # finish up and close ---------------------------------------------------------------------------- #
    print("Success! Modpack updated - Launching your instance now...")


if __name__ == "__main__":
    main()
