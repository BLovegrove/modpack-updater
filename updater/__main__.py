# Imports
import functools
import glob
import os
import pathlib
import zipfile
import requests
import requests
import shutil
from tqdm import tqdm
import toml
from helpers import common
import paramiko

# Make sure we're working in the right dir (updater folder)
program_cwd = os.getcwd()
program_root = os.path.dirname(os.path.abspath(__file__))
if (program_cwd != program_root):
	os.chdir(program_root) 

# Config loading
cfg: dict = toml.load("config.toml")

def download_file(url: str, output: str, description: str = "Progress ", keep_finished: bool = True):
    
    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get('Content-Length', 0))

    path = pathlib.Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else description
    r.raw.read = functools.partial(r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc, leave=keep_finished, ascii="-#") as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)

    return 0

def main():
	# Check a config/mod folder is present
	common.in_minecraft_folder()

	# Make sure there's a temp dir for the program to work in
	if not os.path.isdir("temp"):
		os.mkdir("temp")
	
	# Grab current version by splicing up bcc.json config string
	version_old = ""
	try:
		with open("../config/bcc.json", "r") as f:
			line = f.readline()
			line = line[line.index(":\"v"):]
			version_old = line[3:8]
	except:
		version_old = "unknown"
	
	# Download version file for latest version info
	print(os.linesep + "Getting latest version info...")
	version = ""
	download_file(f"{cfg['pack']['base_url']}/00_version_latest.txt", "temp/00_version_latest.txt")
	with open("temp/00_version_latest.txt", "r") as f:
		version = f.readline()

	# Make sure user knows whats happening
	print(
		os.linesep + 
		f"You are preparing to update your pack from version {version_old} to {version}!" +
		os.linesep
	)
	
	# Check if user still wants to cotinue runing the program
	common.continue_or_not()

	# Download config files
	print(os.linesep + "Downloading config files...")
	download_file(f"{cfg['pack']['base_url']}/configs/config_v{version}.zip", f"temp/config.zip")

	# Clear out old configs...
	print(os.linesep + "Clearing old config files...")
	common.clear_dir("../config/*")

	# Unpack config zip
	print(os.linesep + "Unpacking new config files...")
	with zipfile.ZipFile("temp/config.zip") as zf:
		for member in tqdm(zf.infolist(), desc='Progress ', ascii="-#"):
			try:
				zf.extract(member, "../config/")
				
			except zipfile.error as e:
				pass

	# Compile list of local mods
	mods_local = common.list_items("../mods", False, True)
	
	# Download manifest and generate list of remote mods
	print(os.linesep + "Downloading latest modpack manifest...")
	mods_remote = []
	download_file(f"{cfg['pack']['base_url']}/manifest_v{version}.txt", f"temp/manifest_v{version}.txt")
	with open(f"temp/manifest_v{version}.txt", "r") as f:
		modlist = f.readlines()
		for mod in modlist:
			mods_remote.append(mod.strip("\n").strip("\r"))
	
	# Compare mod lists to see what needs deleting and what needs downloading
	queue_delete = []
	queue_download = []

	# Find mods to delete (diff version or removed completely)
	print(os.linesep + "Finding mods that need deleting...")
	for mod in tqdm(mods_local, desc="Progress ", ascii="-#"):
		if mod in mods_remote:
			continue

		else:
			queue_delete.append(mod)
	
	# Find mods to download (missing from current version)
	print(os.linesep + "Finding mods that need downloading...")
	for mod in tqdm(mods_remote, desc="Progress ", ascii="-#"):
		if mod in mods_local:
			continue

		else:
			queue_download.append(mod)

	# Remove excess mods
	print(os.linesep + "Removing excess mods...")
	for mod in tqdm(queue_delete, desc="Progress ", ascii="-#"):
		os.remove("../mods/" + mod)
	
	# Download missing mods
	print(os.linesep + "Downloading missing mods...")
	for mod in tqdm(queue_download, desc="Progress ", ascii="-#"):
		download_file(f"{cfg['pack']['base_url']}/mods/{mod}", f"../mods/{mod}", f"{mod} ", False)

	# Clean up temp folder
	print(os.linesep + "Cleaning up temp files...")
	common.clear_dir("temp/*")

    # Finish up!
	print(
		os.linesep + 
		"Done! You can now launch the pack. If you experience any technical " +
		"difficulties let your friendly neighbrhood server admin know ASAP!"
	)
    
    # User confirmation dialogue
	print()
	common.continue_or_not("")
    
	return 0

if __name__ == "__main__":
    main()