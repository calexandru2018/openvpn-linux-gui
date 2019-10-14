import os

class FolderManager():
	def __init__(self, dirPath):
		self.dirPath = dirPath

	def returnFolderExist(self, folderName):
		if(os.path.isdir(f"{self.dirPath}/{folderName}")):
			return True
		else:
			return False

	def createFolder(self, folderName):
		if not self.returnFolderExist(folderName): 
			try:
				os.mkdir(self.dirPath + "/" + folderName)
			except:
				return False
			else:
				return True
		else:
			return False

	def deleteFolder(self, folderName):
		if self.returnFolderExist(folderName): 
			
			try:
				os.rmdir(self.dirPath + "/" + folderName)
			except:
				return False
			else:
				return True
		else:
			return False

	