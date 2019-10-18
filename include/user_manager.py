import json, getpass

from include.folder_manager import FolderManager
from include.file_manager import FileManager

class UserManager():
	'''Creates, edits and deletes user data.
	
	Methods
    -------
    create_server_conf():
        Creates a .json file that holds tier and protocol info.
    edit_server_conf():
        Edit .json server configuration file.
    ask_for_server_config():
        Ask the user for input.
	create_user_credentials():	
		Creates a hidden file with users ovpn credentials.
	edit_user_credentials():	
		Edit a users credential file.
	read_user_data():
		Reads user generated files by create_server_conf() and create_user_credentials()
	'''
	def __init__(self, rootDir, user_man_folder_name):
		self.user_server_conf = {'tier': 0, 'protocol': 'udp'}
		self.user_credentials = {'username': '', 'password': ''}
		self.rootDir = rootDir
		self.folder_name = user_man_folder_name
		self.file_server_config_name = 'user_pref'
		self.file_server_config_type = 'json'
		self.file_user_credentials_type = 'user_credentials' # It is actually .user_credentials but I already take care of the dot inside the FileManager() class
		self.folder_manager = FolderManager(self.rootDir)
		self.file_manager = FileManager(self.rootDir)

	# Create server configuration (tier, protocol)
	def create_server_conf(self):
		if not self.file_manager.returnFileExist(self.folder_name, self.file_server_config_name, self.file_server_config_type):
			self.ask_for_server_config()
			if self.folder_manager.returnFolderExist(self.folder_name) or self.folder_manager.createFolder(self.folder_name):
				if self.file_manager.createFile(self.folder_name, self.file_server_config_name, self.file_server_config_type, json.dumps(self.user_server_conf, indent=2)):
					return True
				print("Unable to create file")
				return False
			print("unable to create folder")
			return False
		#print("Conf files already exists")
		return False		

	# Edit server configuration .json file
	def edit_server_conf(self):
		if self.file_manager.returnFileExist(self.folder_name, self.file_server_config_name, self.file_server_config_type):
			out = json.loads(self.file_manager.readFile(self.folder_name, self.file_server_config_name, self.file_server_config_type))
			print("Your config file has stored: ", out)
			while True:
				userInput = input("Would you like to edit your data ? [y/n]: ")

				if userInput[0].lower() == 'n':
					break
				
				self.ask_for_server_config()
				
				if self.file_manager.deleteFile(self.folder_name, self.file_server_config_name, self.file_server_config_type):
					if self.file_manager.createFile(self.folder_name, self.file_server_config_name, self.file_server_config_type,  json.dumps(self.user_server_conf, indent=2)):
						return True
				print(f"Unable to edit, unable to find folder {self.folder_name} and/or file {self.file_server_config_name}")
				continue
		else:
			print("There are no config files to edit.")

	# Create hidden file with users credentials
	def create_user_credentials(self):
		if not self.file_manager.returnFileExist(self.folder_name, "", self.file_user_credentials_type):
			self.ask_for_user_credentials()
			user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
			if self.folder_manager.createFolder(self.folder_name):
				if self.file_manager.createFile(self.folder_name, "", self.file_user_credentials_type, user_cred):
					return True
				print("Unable to create file.")
				return False
			print(f"Unable to create folder. Check if folder {self.folder_name} is present.")
			return False
		print("There is already an existing user, edit it instead.")
		return False

	def edit_user_credentials(self):
		if self.file_manager.returnFileExist(self.folder_name, "", self.file_user_credentials_type):
			self.ask_for_user_credentials()
			user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
			if self.file_manager.deleteFile(self.folder_name, "", self.file_user_credentials_type):
				if self.file_manager.createFile(self.folder_name, "", self.file_user_credentials_type, user_cred):
					return True
				print(f"Unable to edit, unable to find folder {self.folder_name} and/or file {self.file_server_config_name}")
				return False
			print("unable to Delete file")
			return False
		print("The file does not exist")
		return False

	def read_user_data(self, is_user_credentials=False):
		'''Read user data, it either gets the user credentials or the server configurations set by the user.

		Params:
		------
		`is_user_credentials`:
			If True then return ovpn credentials, otherwise return server confs.
		'''
		file_name = self.file_server_config_name
		appropriate_file_extension = self.file_server_config_type
		if is_user_credentials:
			appropriate_file_extension = self.file_user_credentials_type
			file_name = ""

		if self.file_manager.returnFileExist(self.folder_name, file_name, appropriate_file_extension):
			return self.file_manager.readFile(self.folder_name, file_name, appropriate_file_extension)
		return False

	# Check if user exists (both files should be True to return True)
	def check_if_user_exist(self):
		'''Checks if both server conf file and user credential file is generated

		Returns:
		-------
		Bool:
			Return True if both file exists, False otherwise.
		'''
		if self.file_manager.returnFileExist(self.folder_name, self.file_server_config_name, self.file_server_config_type):
			if self.file_manager.returnFileExist(self.folder_name, "", self.file_user_credentials_type):
				return True
			print("Missing user credentials")
		#print("Missing user server configuration file (.json)")
		return False

	def ask_for_user_credentials(self):
		self.user_credentials['username']  = input("Type in your username: ")
		self.user_credentials['password'] = getpass.getpass("Type in your password: ")

	# Ask the user for input
	def ask_for_server_config(self):
		while True: 
			try:
				self.user_server_conf['tier'] = int(input("Type in your tier ([1]-Free, [2]-Basic, [3]-Plus, [4]-Visionary): "))
				if((self.user_server_conf['tier']-1) >= 0 and (self.user_server_conf['tier']-1) <= 3):
					# print("Data saved")
					break
			except:
				print("Incorrect, the tier should be between 1-4, try again.")
				continue
		while True:
			try:
				protocol_input = input("Which protocol to use ? [default udp/tcp]: ")
				if(protocol_input == 'udp' or protocol_input == 'tcp' or protocol_input.strip() == ''):
					self.user_server_conf['protocol'] = "udp" if protocol_input.strip() == "" else protocol_input
					break
			except:
				print("Incorrect protocol")
				continue
	
	def ask_what_to_edit(self):
		while True:
			user_decision = input("What would you like to edit ? [user/server] 0 - exit: ").lower()
			if(user_decision == "user"):
				self.edit_user_credentials()
				break
			elif(user_decision == "server" or user_decision[0] == "s"):
				self.edit_server_conf()
				break
			elif(int(user_decision) == 0):
				break

