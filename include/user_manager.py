import json
from os import getcwd

from include.folder_manager import FolderManager
from include.file_manager import FileManager

class UserManager():
	'''Creates, edits and deletes user data.
	
	Methods
    -------
    createUser():
        Create a new user.
    editUser():
        Edit existing user.
    askForInput():
        Ask the user for input.
	'''
	def __init__(self, rootDir):
		self.userData = {'username': '', 'password': '', 'tier': 0, 'protocol': 'udp'}
		self.rootDir = rootDir
		self.folderName = 'protonvpn_conf'
		self.fileName = 'proton_ovpn_credentials'
		self.fileType = 'json'
		self.folderManager = FolderManager(self.rootDir)
		self.fileManager = FileManager(self.rootDir)
	
	# Create user
	def createUser(self):
		if not self.checkUserExists():
			self.askForInput()
			if self.folderManager.createFolder(self.folderName):
				if self.fileManager.createFile(self.folderName, self.fileName, self.fileType, json.dumps(self.userData, indent=2)):
					return True
				print("Unable to create file")
				return False
			print("unable to create folder")
			return False
		print("User already exists")
		return False		

	# Edit user
	def editUser(self):
		if self.checkUserExists():
			out = json.loads(self.fileManager.readFile(self.folderName, self.fileName, self.fileType))
			print("Your config file has stored: ", out)
			while True:
				userInput = input("Would you like to edit your data ? [y/n]: ")

				if userInput[0].lower() == 'n':
					break
				
				self.askForInput()
				
				if self.fileManager.deleteFile(self.folderName, self.fileName, self.fileType):
					if self.fileManager.createFile(self.folderName, self.fileName, self.fileType,  json.dumps(self.userData, indent=2)):
						return True
				print(f"Unable to edit, unable to find folder {self.folderName} and/or file {self.fileName}")
				continue
		else:
			print("There are no config files to edit.")

	# Check if user exists
	def checkUserExists(self):
		if self.fileManager.returnFileExist(self.folderName, self.fileName, self.fileType):
			return True
		return False

	# Ask the user for input
	def askForInput(self):
		self.userData['username'] = input("Type in your username: ")
		self.userData['password'] = input("Type in your password: ")
		while True: 
			try:
				self.userData['tier'] = int(input("Type in your tier (1-4): "))
				if(self.userData['tier'] >= 1 and self.userData['tier'] <= 4):
					# print("Data saved")
					break
			except:
				print("Incorrect, the tier should be between 1-4, try again.")
				continue
		while True:
			try:
				protocol_input = input("Which protocol to use ? [default udp/tcp]: ")
				if(protocol_input == 'udp' or protocol_input == 'tcp' or protocol_input.strip() == ''):
					self.userData['protocol'] = "udp" if protocol_input.strip() == "" else protocol_input
					break
			except:
				print("Incorrect protocol")
				continue
			
			