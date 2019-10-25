import os, shutil, subprocess

def walk_to_file(path, file, is_return_bool=True, in_dirs=False):
	"""Searches for a file by either looking into subdirectories or comparing filenames

	Returns:
	-------
	Can either return Bool or Path To File.

	"""
	for root, dirs, files in os.walk(path):
		if not in_dirs:
			if file in files:
				if not is_return_bool:
					return os.path.join(root, file)
				else:
					return True
			else:
				return False
		else:
			if file in dirs:
				if not is_return_bool:
					return os.path.join(root, file)
				else:
					return True
			else:
				return False

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

	if not folder_exist(path): 
		#print(path)
		try:
			newFile = open(path, "w+")
			newFile.write(content)
		except:
			return False
		else:
			newFile.close()
			return True
	else:
		return False

def edit_file(path, content):
	'''Edits the specified file, first checking if it exists.
	
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
	if folder_exist(path): 
		try:
			existingFile = open(path, "a+")
			existingFile.write(content)
		except:
			return False
		else:
			existingFile.close()
			return True
	else:
		return False

def read_file(path, file):
	'''Reads the specified file.
	
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
	bool(uknown ?):
		Returns the content if file exists and can be read from, False otherwise.
	'''
	if folder_exist(path): 
		try:
			file = open(path+file, "r")
			return file.read()
		except:
			return False
		else:
			file.close()
	else:
		print("____")
		return False

def delete_file(path, file):
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
	if folder_exist(path):  
		try:
			os.remove(path+file)
		except:
			return False
		else:
			return True
	else:
		return False

import os, shutil

def folder_exist(path):
	if(os.path.isdir(path)):
		return True
	else:
		return False

def create_folder(path):
	#print("Folder created in : ", self.dirPath + "/" + folderName)
	if not folder_exist(path): 
		try:
			os.mkdir(path)
			return True
		except:
			return False
	else:
		return False

def delete_folder_recursive(path):
	if folder_exist(path): 
		try:
			shutil.rmtree(path)
			return True
		except:
			return False
	else:
		return False

def auto_select_optimal_server(data):
	highestScore = 0
	connectToID = ''
	for server in data['serverList']:
		if (data['serverList'][server]['score'] >= highestScore) and (int(data['serverList'][server]['tier']) == 1):
			highestScore = data['serverList'][server]['score']
			connectToID = data['serverList'][server]['id']
	connectInfo = (connectToID, highestScore)
	return connectInfo

def to_ascii(byteValue):
	if byteValue:
		return byteValue.decode('ascii')
	return False

def cmd_command(*args, return_output=True, as_sudo=False, as_bash=False):
	# try:
	if(not return_output and subprocess.run(args[0], stdout=subprocess.PIPE)):
		return True
	else:
		try:
			if as_sudo:
				args[0].insert(0, "sudo")
				x = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			else:
				x = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

			return to_ascii(x.stdout).strip()
		except:
			return False