import os
import platform
import zipfile
from helpers import common
import toml
import paramiko
from tqdm import tqdm
	

# Config loading
cfg = toml.load("config.toml")

# Make sure we're working in the right dir (uploader folder).
program_cwd = os.getcwd()
program_root = os.path.dirname(os.path.abspath(__file__))
print(f"CWD: {program_cwd}, ROOT: {program_root}")
if (program_cwd != program_root):
	os.chdir(program_root)

# Upload local file to remote server defined in config.toml
def upload_file(
	sftp: paramiko.SFTPClient, 
	filepath_local: str, 
	filename_remote: str, 
	description: str = "Progress ", 
	keep_finished: bool = True):
	
	# Move to upload folder dir
	sftp.chdir(cfg['upload']['filepath'])

	# Pretty progress bar for the file upload
	with tqdm(
		desc=description, 
		unit='iB', 
		unit_scale=True, 
		unit_divisor=1024,
		ascii="-#",
		leave=keep_finished) as progress_bar:

		def progress(amount, total):
			progress_bar.total = total
			progress_bar.update(amount - progress_bar.n)

		sftp.put(filepath_local, filename_remote, callback=progress)
	
	return 0

def main():
	# Check a config/mod folder is present
	common.in_minecraft_folder()

	# SSH / SFTP connection setup
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(
		cfg['upload']['host'], 
		cfg['upload']['port'],
		username=cfg['upload']['username'], 
		password=cfg['upload']['password']
	)

	sftp = ssh.open_sftp()

	# Make sure there's a temp dir for the program to work in
	if not os.path.isdir("temp"):
		os.mkdir("temp")
	
	# Make sure user knows whats happening
	print(
		f"You are preparing to upload a new version of {cfg['pack']['name']}!" +
		os.linesep
	)
	
	# Check if user still wants to cotinue runing the program
	common.continue_or_not()
	
	version = common.version_decode(cfg['pack']['version'])
	while True:
		version_input = input(
			os.linesep +
			"Please enter a semantic version type to increase by 1 for this upload. (M)ajor, (m)inor (p)atch or a custom number with (c)ustom." +
			os.linesep +
			"> "
		)

		if version_input in ["M", "m", "p", "c"]:
			break
		elif version_input.lower() in ["major", "minor", "patch", "custom"]:
			version_input = version_input.lower()
			break
		else:
			print(f"{os.linesep}Please enter a valid option (full words or short-codes in backets. Short-codes are case-sensitive).{os.linesep}")
	
	# Update version number
	match version_input:
		case "M" | "major":
			version[0] += 1

		case "m" | "minor":
			version[1] += 1

		case "p" | "patch": 
			version[2] += 1

		case "c" | "custom":
			while True:
				version_custom = input(
					"Enter your custom semantic version (e.g. 1.2.3):" +
					os.linesep +
					"> "
				)

				# Keep repeating if whatever is entered cant be decoded
				try:
					version = common.version_decode(version_custom)
					break
				except Exception as e:
					print(e)
    
	version = common.version_encode(version[0], version[1], version[2])

	print(f"{os.linesep}Updating config file with new version number...")
	cfg['pack']['version'] = version
	with open('config.toml', 'w') as f:
		toml.dump(cfg, f)

	# Alter bcc.json with new version number
	print(os.linesep + "Altering BetterCompat bcc.json file with new version...")
	with open("../config/bcc.json", "w") as f:
		f.write('{"projectID":461725,"modpackName":"LAMZPack 1.18.2","modpackVersion":"v' + version + '","useMetadata":false}')

	# Create list of mods and adding to manifest
	print(os.linesep + "Building mod manifest...")
	with open(f"temp/manifest_v{version}.txt", "w+") as f:
		f.write(os.linesep.join(common.list_items("../mods", False, True)))

	# Zip up config files
	print(os.linesep + "Zipping config files...")
	for file in tqdm(common.list_items("../config", False), desc="Progress ", ascii="-#"):
		try:
			zipfile.ZipFile(f"temp/config_v{version}.zip", mode="a").write(file, file.replace("../config/", ""))
		except:
			print(file)

	# Upload manifests
	print(os.linesep + "Uploading mod manifest file...")
	upload_file(sftp, f"temp/manifest_v{version}.txt", f"manifest_v{version}.txt")

	# Upload configs
	print(os.linesep + "Uploading config ZIP...")
	upload_file(sftp, f"temp/config_v{version}.zip", f"configs/config_v{version}.zip")

	# Upload mod files
	print(os.linesep + "Uploading mod files...")
	with open(f"temp/manifest_v{version}.txt", "r") as f:

		# Track numbers for printout at the end
		files_skipped = 0
		files_uploaded = 0
		lines = f.readlines()

		# Iterate through each line of the manifest
		for line in tqdm(lines, desc="Files uploaded ", ascii="-#"):
			line_clean = line.strip(os.linesep)

			# If the file is alread in remote, track that outcome and start the next loop
			if (common.remote_exists(sftp, f"mods/{line_clean}")):
				files_skipped += 1
				continue
			
			# Upload the file and track that outcome
			upload_file(sftp, f"../mods/{line_clean}", f"mods/{line_clean}", os.path.basename(line_clean), False)
			files_uploaded += 1

		# If some files got uploaded show the number vs total files
		if (files_uploaded != 0):
			print(f"Files uploaded to remote: {files_uploaded} / {len(lines)}")

		# If some files were already in remote, show the number vs. total files
		if (files_skipped != 0):
			print(f"Files already in remote: {files_skipped} / {len(lines)}")

	# Upload version text doc to show latest version number
	print(os.linesep + "Uploading version document...")
	with open("temp/00_version_latest.txt", "w+") as f:
		f.write(version)

	upload_file(sftp, "temp/00_version_latest.txt", "00_version_latest.txt")

	# Clean up temp folder
	print(os.linesep + "Cleaning up temp files...")
	common.clear_dir("temp/*")

	# Close SFTP connection
	sftp.close()
	ssh.close()
    
    # User confirmation dialogue
	print()
	common.continue_or_not(" ")

	return 0

if __name__ == "__main__":
	try:
		main()

	except SystemExit:
		pass

	except Exception as e:
		print(e)
		common.continue_or_not()