import json
from os import getcwd

from include.folder_manager import FolderManager
from include.file_manager import FileManager

class UserManager():
	def __init__(self):
		self.userData = {'username': '', 'password': '', 'tier': 0}
		self.dirPath = getcwd()
		self.fileManagerInfo = {'folderName': 'protonvpn_conf', 'fileName': 'proton_ovpn_credentials', 'fileType': 'json'}
		self.folderManager = FolderManager(self.dirPath)
		self.fileManager = FileManager(self.dirPath)
	
	#Create user
	def createUser(self):
		self.askForInput()

		if not self.folderManager.returnFolderExist(self.fileManagerInfo['folderName']):
			self.folderManager.createFolder(self.fileManagerInfo['folderName'])
		if not self.fileManager.returnFileExist(self.fileManagerInfo['folderName'], self.fileManagerInfo['fileName'], self.fileManagerInfo['fileType']):
			self.fileManager.createFile(self.fileManagerInfo['folderName'], self.fileManagerInfo['fileName'], self.fileManagerInfo['fileType'], json.dumps(self.userData, indent=2))		

	#Edit user
	def editUser(self):
		if self.fileManager.returnFileExist(self.fileManagerInfo['folderName'], self.fileManagerInfo['fileName'], self.fileManagerInfo['fileType']):
			out = json.load(self.fileManager.readFile(self.fileManagerInfo['folderName'], self.fileManagerInfo['fileName'], self.fileManagerInfo['fileType']))
			print("Your config file has stored: ", out)
		else:
			print("There are no config files.")

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