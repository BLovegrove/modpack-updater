# Imports
import os
import sys
import requests
import requests
import shutil
import zipfile
from tqdm.auto import tqdm
import toml

# Config loading
cfg: dict = toml.load("./config.toml")

# Deletes target regardless of file or folder status
def rm_file_folder(target):
    
    if os.path.isfile(target):
        os.remove(target)
    else:
        # rmtree remves diirectory ad *all* contnents
        shutil.rmtree(target)

    return 0

# Generate list of all files / folders in target directory 
def list_items(target_dir):
    
    files = []
    folders = []
    # Walks through dir getting filenames and foldernames seperately
    for root, subfolder, filenames in os.walk(target_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))
        
        folders.append(root)
    
    # Flips order of folders to avoid 'not empty' error.    
    folders.reverse()

    # Assembles both lists into one, deleting files first and folders last
    items = files + folders
    
    return items

# scans for the folders the program needs to run. Kills the program if nothing is found.
def in_minecraft_folder():
    
    if os.path.isdir("../config") and os.path.isdir("../mods"):
        return
    
    else:
        print("Minecraft folder not detected! Make sure you put the 'updater' folder in your Minecraft folder.")
        continue_or_not()
        sys.exit(0)
    

def continue_or_not():
    while True:
        reply: str = input(f"Would you like to continue? Enter (y)es to proceed or anything else to cancel: {os.linesep}> ")
        
        if reply.lower() == "y" or reply.lower == "yes":
            break
        
        else:
            sys.exit(0)    
    
    return 0

# Downloads assets from your packs host
def update_download(url):
    
    # Make a ./temp directory if it doesnt exist
    if (not os.path.isdir("temp")):
        os.mkdir("temp")
    
    # Make an HTTP request within a context manager
    with requests.get(url, stream=True) as r:
        
        # Check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        
        # Implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="Progress ") as raw:
        
            # Save the output to a file
            with open("temp/modpack.zip", 'wb') as output:
                shutil.copyfileobj(raw, output)

def update_apply(src_dir, dst_dir):
    
    items = list_items(dst_dir)
    
    # Wipes / recreates all files / folders in relevant directories
    for file in tqdm(items, desc="Deleting files "):
        if os.path.isfile(file):
            os.remove(file)
        else:
            os.rmdir(file)
        
    print(f"Re-creating directory...")
    os.mkdir(dst_dir)
    
    # Copies over remote files / folders
    for item in tqdm(os.listdir(src_dir), desc="Copying from remote "):
        
        item_abs = os.path.join(src_dir, item)
        
        if os.path.isfile(item_abs):
            shutil.copy2(item_abs, dst_dir)
        else:
            shutil.copytree(item_abs, dst_dir + f"/{item}")
    
    return 0

def main():
    
    # MC folder check
    in_minecraft_folder()
    
    # Welcome message
    print(
        f"Thank you for choosing {cfg['pack_name']}!" +
        (os.linesep * 2) +
        f"Please make sure you have this program in your packs Minecraft folder " +
        "with a shortcut to it placed somewhere else before continuing." +
        os.linesep +
        "(If this is a fresh install - you probably don't have to worry about this.)" +
        os.linesep
    )
    
    # User confirmation dialogue
    continue_or_not()
    
    print(f"{os.linesep}Downloading the latest version of the pack...{os.linesep}")
    
    # Get remote zip
    update_download(cfg['pack_url'])
        
    print(f"{os.linesep}Unpacking update zip...{os.linesep}")
    
    # Make ./temp/unpacked if it doesnt exist
    if (not os.path.isdir("temp/unpacked")):
        os.mkdir("temp/unpacked")
    
    # Unpack zip to ./temp/unpacked
    with zipfile.ZipFile("temp/modpack.zip") as zf:
        for member in tqdm(zf.infolist(), desc='Progress '):
            try:
                zf.extract(member, "temp/unpacked")
                
            except zipfile.error as e:
                pass
        
    print(f"{os.linesep}Matching local with remote data...{os.linesep}")
    
    src_config = "temp/unpacked/config"
    src_mods = "temp/unpacked/mods"
    
    # Update confifg files
    print("Configs: ")
    update_apply(src_config, "../config")
    
    print()
    
    # Update mod files
    print("Mods: ")
    update_apply(src_mods, "../mods")
    
    # Clean up the temp folder 
    print(f"{os.linesep}Cleaning up temporary files...{os.linesep}")
    shutil.rmtree("./temp")
    
    # Finish up!
    print("Done! You can now launch the pack. If you experience any technical difficulties let your friendly neighbrhood server admin know ASAP!")
    
    # User confirmation dialogue
    continue_or_not()
    
    return 0

if __name__ == "__main__":
    main()