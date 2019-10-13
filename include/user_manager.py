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
	def __init__(self):
		self.userData = {'username': '', 'password': '', 'tier': 0}
		self.dirPath = getcwd()
		self.folderName = 'protonvpn_conf'
		self.fileName = 'proton_ovpn_credentials'
		self.fileType = 'json'
		self.folderManager = FolderManager(self.dirPath)
		self.fileManager = FileManager(self.dirPath)
	
	# Create user
	def createUser(self):
		self.askForInput()

		if not self.folderManager.returnFolderExist(self.folderName):
			self.folderManager.createFolder(self.folderName)
		if not self.fileManager.returnFileExist(self.folderName, self.fileName, self.fileType):
			self.fileManager.createFile(self.folderName, self.fileName, self.fileType, json.dumps(self.userData, indent=2))		

	# Edit user
	def editUser(self):
		if self.checkUserExists:
			out = json.load(self.fileManager.readFile(self.folderName, self.fileName, self.fileType))
			print("Your config file has stored: ", out)
			while True:
				userInput = input("Would you like to edit your data ? [y/n]: ")

				if userInput[0].lower() == 'n':
					break
				
				self.askForInput()
				
				if self.fileManager.deleteFile(self.folderName, self.fileName, self.fileType):
					if self.fileManager.createFile(self.folderName, self.fileName, self.fileType,  json.dumps(self.userData, indent=2)):
						break
				
				print("Unable to edit")
				continue
		else:
			print("There are no config files.")

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
			self.userData['tier'] = int(input("Type in your tier (1-4): "))
			if(self.userData['tier'] >= 1 and self.userData['tier'] <= 4):
				print("Data saved")
				break
			else:	
				print("Incorrect, the tier should be between 1-4, try again.")
				continue