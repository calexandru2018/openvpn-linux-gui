import os

class FileManager():
	def __init__(self, dirPath):
		self.dirPath = dirPath

	def returnFileExist(self, folderName, fileName, fileType):
		'''Checks if file exists in specified folder.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		Returns:
		-------
		bool:
			Returns True if file exists, False otherwise.
		'''
		if(os.path.isfile(f"{self.dirPath}/{folderName}/{fileName}.{fileType}")):
			return True
		else:
			return False

	def createFile(self, folderName, fileName, fileType, contentToWrite):
		'''Creates the file and writes content to it.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		`contentToWrite`:
			The content to write to file.
		
		Returns:
		-------
		bool:
			Returns True if file is created, False otherwise.
		'''

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
		'''Edits the specified file, first checking if it exists.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		`contentToWrite`:
			The content to write to file.
		
		Returns:
		-------
		bool:
			Returns True if file is created, False otherwise.
		'''
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

	def readFile(self, folderName, fileName, fileType):
		'''Reads the specified file.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		
		Returns:
		-------
		bool(uknown ?):
			Returns the content if file exists and can be read from, False otherwise.
		'''
		if self.returnFileExist(folderName, fileName, fileType): 
			try:
				file = open(self.dirPath + "/" + folderName +  "/" + fileName + "." + fileType, "r")
				return file.read()
			except:
				return False
			else:
				existingFile.close()
		else:
			return False

	def deleteFile(self, folderName, fileName, fileType):
		'''Deletes the specified file.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		
		Returns:
		-------
		bool:
			Returns True if file exists and can be deleted, False otherwise.
		'''
		if self.returnFileExist(folderName, fileName, fileType):  
			try:
				os.remove(self.dirPath + "/" + folderName +  "/" + fileName + "." + fileType)
			except:
				return False
			else:
				return True
		else:
			return False