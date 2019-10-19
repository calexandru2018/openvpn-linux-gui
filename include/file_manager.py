import os

class FileManager():

	def returnFileExist(self, path):
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
		if(os.path.isfile(path)):
			return True
		else:
			return False

	def createFile(self, path, content):
		'''Creates the file and writes content to it.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		`content`:
			The content to write to file.
		
		Returns:
		-------
		bool:
			Returns True if file is created, False otherwise.
		'''

		if not self.returnFileExist(path): 
			#print(path)
			try:
				newFile = open(path, "w+")
				newFile.write(content)
			except:
				return False
			else:
				newFile.close()
				return True
		else:
			return False

	def editFile(self, path, content):
		'''Edits the specified file, first checking if it exists.
		
		Parameters:
		----------
		`folderName` : string
			The name of the folder.
		`fileName` : string
			The name of the file.
		`fileType` : string
			The type/extension - json or txt.
		`content`:
			The content to write to file.
		
		Returns:
		-------
		bool:
			Returns True if file is created, False otherwise.
		'''
		if self.returnFileExist(path): 
			try:
				existingFile = open(path, "a+")
				existingFile.write(content)
			except:
				return False
			else:
				existingFile.close()
				return True
		else:
			return False

	def readFile(self, path):
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
		if self.returnFileExist(path): 
			try:
				file = open(path, "r")
				return file.read()
			except:
				return False
			else:
				file.close()
		else:
			return False

	def deleteFile(self, path):
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
		if self.returnFileExist(path):  
			try:
				os.remove(path)
			except:
				return False
			else:
				return True
		else:
			return False