import os

class FileManager():
	def __init__(self, dirPath):
		self.dirPath = dirPath

	def returnFileExist(self, folderName, fileName, fileType):
		if(os.path.isfile(f"./{folderName}/{fileName}.{fileType}")):
			return True
		else:
			return False

	def createFile(self, folderName, fileName, fileType, contentToWrite):
		if not self.returnFileExist(folderName, fileName, fileType): 
			
			try:
				newFile = open(self.dirPath + "/" + folderName +  "/" + fileName + "." + fileType, "w+")
				newFile.write(contentToWrite)
			except:
				return False
			else:
				newFile.close()
				return True
		else:
			return False

	def editFile(self, folderName, fileName, fileType, contentToWrite):
		if self.returnFileExist(folderName, fileName, fileType): 
			
			try:
				existingFile = open(self.dirPath + "/" + folderName +  "/" + fileName + "." + fileType, "a+")
				existingFile.write(contentToWrite)
			except:
				return False
			else:
				existingFile.close()
				return True
		else:
			return False

	def deleteFile(self, folderName, fileName, fileType):
		if self.returnFileExist(folderName, fileName, fileType):  
			
			try:
				os.remove(self.dirPath + "/" + folderName +  "/" + fileName + "." + fileType)
			except:
				return False
			else:
				return True
		else:
			return False