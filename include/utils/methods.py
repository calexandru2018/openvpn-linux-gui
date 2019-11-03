import os, shutil, subprocess, requests, re

from include.utils.constants import (
	PROTON_CHECK_URL, PROTON_HEADERS, DYNDNS_CHECK_URL
)

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

	# if folder_exist(path): 
	try:
		existingFile = open(path, write_to)
		existingFile.write(content)
	except:
		return False
	else:
		existingFile.close()
		return True
	# else:
	# 	return False

def read_file(path, second_arg=False):
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
	# if folder_exist(path): 
	if not second_arg:
		try:
			file = open(path, "r")
			return file.read()
		except:
			return False
		else:
			file.close()
	else:
		try:
			file = open(path+"/"+second_arg, "r")
			return file.read()
		except:
			return False
		else:
			file.close()
	# else:
	# 	print("____")
	# 	return False

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
	# if folder_exist(path):  
	try:
		os.remove(path)
		return True
	except:
		return False
	# else:
	# 	return False

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

def auto_select_optimal_server(data, tier):
	"""Returns a tuple with information abou the most optimal server.
	Returns:
	-------
	tuple (connection_ID, best_score, server_name) 
	"""
	best_score = 999
	connection_ID = ''
	server_name = ''
	for server in data['serverList']:
		if (data['serverList'][server]['score'] < best_score) and (int(data['serverList'][server]['tier']) == tier):
			server_name = data['serverList'][server]['name']
			connection_ID = data['serverList'][server]['id']
			best_score = data['serverList'][server]['score']
	connectInfo = (connection_ID, best_score, server_name)
	return connectInfo

def to_ascii(byteValue):
	if byteValue:
		return byteValue.decode('ascii')
	return False

def cmd_command(*args, return_output=True, as_sudo=False, as_bash=False):
	if(not return_output and subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).returncode == 0):
		return True
	else:
		try:
			if as_sudo:
				args[0].insert(0, "sudo")
				output = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			else:
				output = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

			return to_ascii(output.stdout).strip()
		except:
			return False

# check for ip: get_ip()
def get_ip():
	'''Gets the host IP from two different sources and compares them.
	
	Returns:
	-------
	Bool:
		True if the IP's match, False otherwise.
	'''
	dyndnsRequest = requests.get(DYNDNS_CHECK_URL)
	dyndnsIp = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", dyndnsRequest.text)[0].strip()

	protonRequest = requests.get(PROTON_CHECK_URL, headers=(PROTON_HEADERS)).json()

	if dyndnsIp == protonRequest['IP']:
		#print("Internet is OK and your IP is:", dyndnsIp)
		return protonRequest['IP']
	return False