import sys
from packaging import version
import os
import pathlib
from urllib.parse import urlsplit
from tkinter import messagebox
import requests
import toml

import config as cfg


def main():
    sys.argv[0] = "/home/brandon/Documents/modpack-updater/update/"

    try:
        script_dir = (
            sys.argv[0].replace("\\modpack-update.exe", "")
            # .replace("modpack-update", "")
        )

        os.chdir(script_dir)
    except Exception as e:
        message = (
            f"{e}"
            + f"Args found: {sys.argv}"
            + os.linesep * 2
            + "Please provide the full path to this executable as an arg to run the updater."
            + os.linesep * 2
            + "If done via your launcher, this should be the first arg by default."
        )
        messagebox.showerror(title="No arguments given!", message=message)
        return

    # Welcome message
    print(
        f"# ---------------------------------------------- #{os.linesep}"
        + f"#                 Modpack Update                 #{os.linesep}"
        + f"# ---------------------------------------------- #{os.linesep}"
        + os.linesep
        + f"Thank you for choosing {cfg.pack.name}!{os.linesep*2}"
    )

    # TODO: check client can see server
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
        print("Connection status: ✅" + os.linesep)

    # TODO: check current version against most recent remote version

    changelog = toml.loads(
        requests.get(cfg.pack.url + "/changelog.toml", stream=True).content.decode()
    )

    current_version = pathlib.Path("../version.txt").read_text()
    update_queue: list[dict[str, str]] = []

    for update in changelog["updates"]:
        if version.parse(update["version"]) > version.parse(current_version):
            update_queue.append(update)

    if len(update_queue) <= 0:
        messagebox.showinfo(
            title="Modpack up to date!",
            message="Your instance should launch shortly...",
        )
        return

    print("Update detected! Collating changes since last update..." + os.linesep)

    # TODO: parse changes into add and remove lists

    process_queue: list[dict[str, str]] = []
    rem_queue = []
    add_queue = []

    for update in update_queue:
        for key in update.keys():
            if key == "version":
                continue

            try:
                for item in update[key]["rem"]:
                    if item not in rem_queue:
                        rem_queue.append(item)
                        process_queue.append({"action": "rem", "file": item})
            except KeyError as e:
                pass

            try:
                for item in update[key]["add"]:
                    if item not in add_queue:
                        add_queue.append(item)
                        process_queue.append({"action": "add", "file": item})
            except KeyError as e:
                pass

    # TODO: execute process queue downloading and deleting files where needed

    for item in process_queue:
        queue_display = f"(item #{process_queue.index(item)+1} of {len(process_queue)})"

        file = item["file"]

        if file.split(".")[-1] == "jar":
            item_type = "mods"
        else:
            item_type = "config"

        filepath = f"../{item_type}/{file}"

        if item["action"] == "rem":
            try:
                print(f"Removing '{file}' {queue_display}")
                os.remove(filepath)
            except FileNotFoundError as e:
                print(f"File not found. Can't remove.")
        else:
            print(f"Creating '{file}' {queue_display}")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            if os.path.exists(filepath):
                os.remove(filepath)

            with open(filepath, "wb") as f:
                f.write(requests.get(f"{cfg.pack.url}/{item_type}/{file}").content)

    # TODO: change local version to match remote

    with open("../version.txt", "w") as f:
        f.write(update_queue[0]["version"])

    # TODO: finish up and close
    messagebox.showinfo(
        title="Success!",
        message=f"Modpack updated.{os.linesep*2}Launching your instance now...",
    )


if __name__ == "__main__":
    main()