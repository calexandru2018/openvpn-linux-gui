import os, shutil

class FolderManager():
	def returnFolderExist(self, path):
		if(os.path.isdir(path)):
			return True
		else:
			return False

	def createFolder(self, path):
		#print("Folder created in : ", self.dirPath + "/" + folderName)
		if not self.returnFolderExist(path): 
			try:
				os.mkdir(path)
				return True
			except:
				return False
		else:
			return False

	def deleteFolder(self, path):
		if self.returnFolderExist(path): 
			try:
				os.rmdir(path)
				return True
			except:
				return False
		else:
			return False

	def delete_folder_recursive(self, path):
		if self.returnFolderExist(path): 
			try:
				shutil.rmtree(path)
				return True
			except:
				return False
		else:
			return False

	