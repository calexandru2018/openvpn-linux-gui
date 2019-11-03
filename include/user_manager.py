import json, getpass

from include.utils.constants import (USER_FOLDER, USER_CRED_FILE, USER_PREF_FILE, USER_FOLDER, USER_CRED_FILE, USER_PREF_FILE)
from include.utils.methods import (walk_to_file, create_file, read_file, edit_file, delete_file, create_folder,folder_exist)

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
	def __init__(self):
		self.user_server_conf = {'tier': 0, 'protocol': 'udp'}
		self.user_credentials = {'username': '', 'password': ''}

	# Create server configuration (tier, protocol)
	def create_server_conf(self):
		if not walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			self.ask_for_server_config()
			if folder_exist(USER_FOLDER) or create_folder(USER_FOLDER):
				if create_file(USER_PREF_FILE, json.dumps(self.user_server_conf, indent=2)):
					return True
				print("Unable to create file")
				return False
			print("unable to create folder")
			return False
		#print("Conf files already exists")
		return False		

	# Edit server configuration .json file
	def edit_server_conf(self):
		if walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			user_pref = json.loads(read_file(USER_PREF_FILE))
			print("Your config file has stored: ", user_pref)
			while True:
				userInput = input("Would you like to edit your data ? [y/n]: ")

				if userInput[0].lower() == 'n':
					break
				
				self.ask_for_server_config()
				
				user_pref['tier'] = self.user_server_conf['tier']
				user_pref['protocol'] = self.user_server_conf['protocol']

				if edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False):
					return True

				print(f"Unable to edit, unable to find folder {USER_FOLDER} and/or file {USER_PREF_FILE }")
				break
		else:
			print("There are no config files to edit.")

	# Create hidden file with users credentials
	def create_user_credentials(self):
		if not walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
			self.ask_for_user_credentials()
			user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
			if create_folder(USER_FOLDER):
				if create_file(USER_CRED_FILE, user_cred):
					return True
				print("Unable to create file.")
				return False
			print(f"Unable to create folder. Check if folder {USER_FOLDER} is present.")
			return False
		print("There is already an existing user, edit it instead.")
		return False

	def edit_user_credentials(self):
		if walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
			self.ask_for_user_credentials()
			user_cred = self.user_credentials['username']  + "\n" + self.user_credentials['password'] 
			if delete_file(USER_CRED_FILE):
				if create_file(USER_CRED_FILE, user_cred):
					return True
				print(f"Unable to edit, unable to find folder {USER_FOLDER} and/or file {USER_CRED_FILE}")
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
		file_name = USER_PREF_FILE.split("/")[-1] 
		if is_user_credentials:
			file_name = USER_CRED_FILE.split("/")[-1] 

		if walk_to_file(USER_FOLDER, file_name):
			return read_file(USER_FOLDER, file_name)
		return False

	# Check if user exists (both files should be True to return True)
	def check_if_user_exist(self):
		'''Checks if both server conf file and user credential file is generated

		Returns:
		-------
		Bool:
			Return True if both file exists, False otherwise.
		'''
		if walk_to_file(USER_FOLDER, USER_PREF_FILE.split("/")[-1]):
			if walk_to_file(USER_FOLDER, USER_CRED_FILE.split("/")[-1]):
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
				user_tier = input("Type in your tier ([0]Free, [1]Basic, [2]Plus, [3]Visionary): ")
				if user_tier[0].lower() == "f" or int(user_tier[0]) == 0:
					self.user_server_conf['tier'] = 0
				elif user_tier[0].lower() == "b" or int(user_tier[0]) == 1:
					self.user_server_conf['tier'] = 1
				elif user_tier[0].lower() == "p"  or int(user_tier[0]) == 2:
					self.user_server_conf['tier'] = 2
				elif user_tier[0].lower() == "v" or int(user_tier[0]) == 3:
					self.user_server_conf['tier'] = 3
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

