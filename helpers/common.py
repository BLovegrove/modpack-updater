import os
import shutil
import sys
from tqdm import tqdm

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
		
		if (include_folders):
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
		print("Minecraft folder not detected! Make sure you put the program folder in your Minecraft folder.")
		continue_or_not("")
		sys.exit(0)
	
# prompts user for some input to continue or quit
def continue_or_not(input_message: str = "Would you like to continue?"):
	while True:
		reply: str = input(f"{input_message} Enter (y)es to confirm or anything else to cancel: {os.linesep}> ")
		
		if reply.lower() == "y" or reply.lower == "yes":
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
            shutil.copytree(item_abs, dst_dir + f"/{item}")

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