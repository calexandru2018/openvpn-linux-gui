import json, getpass

from include.utils.constants import (USER_FOLDER, USER_CRED_FILE, USER_PREF_FILE, USER_FOLDER, USER_CRED_FILE, USER_PREF_FILE)
from include.utils.methods import (walk_to_file, create_file, edit_file, delete_file, create_folder,folder_exist)

class UserManager():
	'''Creates, edits and deletes user data.
	
	Methods
    -------
    create_user_pref_file():
        Creates a .json file that holds tier and protocol info.
    edit_server_conf():
        Edit .json server configuration file.
    ask_for_server_config():
        Ask the user for input.
	create_user_credentials_file():	
		Creates a hidden file with users ovpn credentials.
	edit_user_credentials():	
		Edit a users credential file.
	read_user_data():
		Reads user generated files by create_user_pref_file() and create_user_credentials_file()
	'''
	def __init__(self):
		self.user_server_conf = {'tier': 0, 'protocol': 'udp'}
		self.user_credentials = {'username': '', 'password': ''}

	# Create server configuration (tier, protocol)
	def create_user_pref_file(self):
		if walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			#print("Conf files already exists")
			return False	

		self.ask_for_server_config()
		
		if not folder_exist(USER_FOLDER) or not create_folder(USER_FOLDER):
			print("unable to create folder")
			return False

		if not create_file(USER_PREF_FILE, json.dumps(self.user_server_conf, indent=2)):
			print("Unable to ")
			return False

		return True

	# Edit server configuration .json file
	def edit_server_conf(self):
		if not walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			print("Configuration file was not yet setup.")
			return False
		
		with open(USER_PREF_FILE) as file:
			user_pref = json.load(file) 

		print("Your config file has stored: ", user_pref)
		
		while True:
			userInput = input("Would you like to edit your data ? [y/n]: ")

			if userInput[0].lower() == 'n':
				break
			
			self.ask_for_server_config()
			
			user_pref['tier'] = self.user_server_conf['tier']
			user_pref['protocol'] = self.user_server_conf['protocol']

			if not edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False):
				print(f"Unable to edit, unable to find folder {USER_FOLDER} and/or file {USER_PREF_FILE }")
				break
			
			return True

	# Create hidden file with users credentials
	def create_user_credentials_file(self):
		if walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
			print("There is already an existing user, edit it instead.")
			return False

		self.ask_for_user_credentials()
		user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
		
		if not create_folder(USER_FOLDER):
			print(f"Unable to create folder. Check if folder {USER_FOLDER} is present.")
			return False
		
		if not create_file(USER_CRED_FILE, user_cred):
			print("Unable to create file.")
			return False

		return True

	def edit_user_credentials(self):
		if not walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
			print("The file does not exist")
			return False
		
		self.ask_for_user_credentials()
		user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
		
		if not delete_file(USER_CRED_FILE):
			print("unable to Delete file")
			return False

		if not create_file(USER_CRED_FILE, user_cred):
			print(f"Unable to edit, unable to find folder {USER_FOLDER} and/or file {USER_CRED_FILE}")
			return False

		return True

	def read_user_data(self, is_user_credentials=False):
		'''Read user data, it either gets the user credentials or the server configurations set by the user.

		Params:
		------
		`is_user_credentials`:
			If True then return ovpn credentials, otherwise return server confs.
		'''
		file_name = USER_PREF_FILE.split("/")[-1] 
		if is_user_credentials:
			file_name = USER_CRED_FILE.split("/")[-1] 

		user_data = walk_to_file(USER_FOLDER, file_name)

		if not walk_to_file(USER_FOLDER, file_name):
			return False
			
		return user_data

	# Check if user exists (both files should be True to return True)
	def check_if_user_exist(self):
		'''Checks if both server conf file and user credential file is generated

		Returns:
		-------
		Bool:
			Return True if both file exists, False otherwise.
		'''
		if not walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			print("Missing user server configuration file (.json)")
			return False

		if not walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
			print("Missing user credentials")
			return False
		
		return True

	def ask_for_user_credentials(self):
		self.user_credentials['username']  = input("Type in your username: ")
		self.user_credentials['password'] = getpass.getpass("Type in your password: ")

	# Ask the user for input
	def ask_for_server_config(self):
		while True: 
			try:
				user_tier = input("Type in your tier ([0]Free, [1]Basic, [2]Plus, [3]Visionary): ").lower()
				if user_tier[0] == "f" or int(user_tier[0]) == 0:
					self.user_server_conf['tier'] = 0
				elif user_tier[0] == "b" or int(user_tier[0]) == 1:
					self.user_server_conf['tier'] = 1
				elif user_tier[0] == "p"  or int(user_tier[0]) == 2:
					self.user_server_conf['tier'] = 2
				elif user_tier[0] == "v" or int(user_tier[0]) == 3:
					self.user_server_conf['tier'] = 3
				break
			except:
				print("Incorrect, the tier should be between 1-4, try again.")
				continue

		while True:
			try:
				protocol_input = input("Which protocol to use ? [default udp/tcp]: ").lower()
				if(protocol_input == 'udp' or protocol_input == 'tcp' or protocol_input.strip() == ''):
					self.user_server_conf['protocol'] = "udp" if protocol_input.strip() == "" else protocol_input
					break
			except:
				print("Incorrect protocol")
				continue
	
	def ask_what_to_edit(self):
		while True:
			user_decision = input("What would you like to edit ? [user/server] 0 - exit: ").lower()
			if(user_decision == "user" or user_decision[0] == "u"):
				self.edit_user_credentials()
				break
			elif(user_decision == "server" or user_decision[0] == "s"):
				self.edit_server_conf()
				break
			elif(int(user_decision) == 0):
				break

