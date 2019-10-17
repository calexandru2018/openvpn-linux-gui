import os, shutil

class FolderManager():
	def __init__(self, dirPath):
		self.dirPath = dirPath

	def returnFolderExist(self, folderName):
		if(os.path.isdir(f"{self.dirPath}/{folderName}")):
			return True
		else:
			return False

	def createFolder(self, folderName):
		#print("Folder created in : ", self.dirPath + "/" + folderName)
		if not self.returnFolderExist(folderName): 
			try:
				os.mkdir(self.dirPath + "/" + folderName)
				return True
			except:
				return False
		else:
			return False

	def deleteFolder(self, folderName):
		if self.returnFolderExist(folderName): 
			try:
				os.rmdir(self.dirPath + "/" + folderName)
				return True
			except:
				return False
		else:
			return False

	def delete_folder_recursive(self, folderName):
		if self.returnFolderExist(folderName): 
			try:
				shutil.rmtree(self.dirPath + "/" + folderName)
				return True
			except:
				return False
		else:
			return False

	