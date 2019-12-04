import os, shutil, subprocess, requests, re

from include.utils.constants import (
	PROTON_CHECK_URL, PROTON_HEADERS, DYNDNS_CHECK_URL, CACHE_FOLDER
)

from include.logger import log

def walk_to_file(path, file, is_return_bool=True, in_dirs=False):
	"""Searches for a file by either looking into subdirectories or comparing filenames

	Returns:
	-------
	Can either return Bool or Path To File.

	"""
	for root, dirs, files in os.walk(path):
		if not in_dirs:
			if not file in files:
				log.warning(f"\"{file}\" was NOT found in \"{root}\".")
				return False

			log.info(f"\"{file}\" was found in \"{root}\".")

			if is_return_bool:
				return True

			return os.path.join(root, file)
		
		if not file in dirs:
			log.warning(f"\"{file}\" was NOT found in \"{root}\".")
			return False
		
		log.info(f"\"{file}\" was found in \"{root}\".")
		
		if is_return_bool:
			return True

		return os.path.join(root, file)

def create_file(path, content):
	'''Creates the file and writes content to it.
	
	Parameters:
	----------
	`folderName` : string
		The name of the folder.
	`fileName` : string
		The name of the file.
	`fileType` : string
		The type/extension - json or txt.
	`content`:
		The content to write to file.
	
	Returns:
	-------
	bool:
		Returns True if file is created, False otherwise.
	'''
	try:
		newFile = open(path, "w+")
		newFile.write(content)
		newFile.close()
		log.info(f"\"{path}\" was created and succesfully written to.")
		return True
	except:
		log.warning(f"Unable to create \"{path}\".")
		return False

def edit_file(path, content, append=True):
	'''Edits the specified file, first checking if it exists.
	
	Parameters:
	----------
	`path` : string
		Path to file
	`content`:
		The content to write to file.
	`append` : Bool = True
		By default it appends to file (a+), if False the it overwrites (w+)
	
	Returns:
	-------
	bool:
		Returns True if file is created, False otherwise.
	'''
	write_to = "a"
	if not append:
		write_to = "w"

	try:
		existingFile = open(path, write_to)
		existingFile.write(content)
		existingFile.close()
		log.info(f"Content was edited with \"{write_to}\" on: \"{path}\"")
		return True
	except:
		log.warning(f"Unable to edit content with \"{write_to}\" on: {path}")
		return False

def delete_file(path):
	'''Deletes the specified file.
	
	Parameters:
	----------
	`folderName` : string
		The name of the folder.
	`fileName` : string
		The name of the file.
	`fileType` : string
		The type/extension - json or txt.
	
	Returns:
	-------
	bool:
		Returns True if file exists and can be deleted, False otherwise.
	'''
	filename = path.split("/")[-1]
	try:
		os.remove(path)
		log.info(f"File \"{filename}\" was removed.")
		return True
	except:
		log.warning(f"Unable to remove \"{filename}\".")
		return False

def folder_exist(path):
	if not os.path.isdir(path):
		log.info(f"Folder \"{path}\" DOES NOT exist.")
		return False

	log.info(f"Folder \"{path}\" DOES exist.")
	return True

def create_folder(path):
	if folder_exist(path): 
		log.info(f"Folder \"{path}\" already exists.")
		return False

	try:
		os.mkdir(path)
		log.info(f"Folder \"{path}\" was created.")
		return True
	except:
		log.critical(f"Unable to create folder: \"{path}\".")
		return False

def delete_folder_recursive(path):
	if not folder_exist(path): 
		log.warning(f"Could not recursively delete folder: \"{path}\" since it does not exist.")
		return False

	try:
		shutil.rmtree(path)
		log.info(f"Folder \"{path}\" was recursively deleted.")
		return True
	except:
		log.critical(f"Could not recursively delete folder: \"{path}\".")
		return False

def cmd_command(*args, return_bool=False, as_sudo=False, as_bash=False, custom_shell=False, default_shelll=False):
	if(return_bool and subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).returncode == 0):
		return True
	else:
		if as_sudo:
			args[0].insert(0, "sudo")
		
		raw_output = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		if not raw_output.returncode == 0:
			log.warning(f"Unable to run command with following args: {args}")
			log.debug(f"Output: {raw_output}")
			return False
		
		if not return_bool:
			decoded_output = raw_output.stdout.decode('ascii').strip()
			log.debug(f"Sucessful CMD output: {decoded_output}")
			# should return (return_code, output)
			return decoded_output
		return True
		# except: