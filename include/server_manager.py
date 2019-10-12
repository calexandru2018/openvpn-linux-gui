import requests, json
from include.file_manager import FileManager
from include.folder_manager import FolderManager
from os import getcwd

class ServerManger():
	def __init__(self):
		self.dirPath = getcwd()
		self.serverList = {}
		self.serverNameLong = ''
		self.serverNameShort = ''
		self.fileManager = FileManager(self.dirPath)
		self.folderManager = FolderManager(self.dirPath)
		self.folderName = 'protonvpn_server_collection'
		self.countryList =  {
			'AT': 'Austria',
			'AU': 'Australia',
			'BE': 'Belgium',
			'BG': 'Bulgaria',
			'BR': 'Brazil',
			'CA': 'Canada',
			'CH': 'Switzerland',
			'CR': 'Costa Rica',
			'CZ': 'Czechia',
			'DE': 'Germany',
			'DK': 'Denmark',
			'EE': 'Estonia',
			'ES': 'Spain',
			'FI': 'Finald',
			'FR': 'France',
			'HK': 'Hong Kong',
			'IE': 'Ireland',
			'IL': 'Isreael',
			'IN': 'India',
			'IS': 'Iceland',
			'IT': 'Italy',
			'JP': 'Japan',
			'KR': 'Korea',
			'LU': 'Luxembourg',
			'LV': 'Latvia',
			'NL': 'Netherlands',
			'NO': 'Norway',
			'NZ': 'New Zeland',
			'PL': 'Poland',
			'PT': 'Portugal',
			'RO': 'Romania',
			'RS': 'Serbia',
			'RU': 'Russian Federation',
			'SE': 'Sweden',
			'SG': 'Singapore',
			'SK': 'Slovakia',
			'TW': 'Taiwan',
			'UA': 'Ukraine',
			'UK': 'United Kingdom',
			'US': 'United States',
			'ZA': 'South Africa',
		}
		self.collectServerList()
		
	
	def collectServerList(self):
		serverReq = requests.get("https://api.protonmail.ch/vpn/logicals", headers={'User-Agent': 'Custom'}).json()
		for server in serverReq['LogicalServers']:
			if server['EntryCountry'] in self.countryList:
				self.serverNameLong = self.countryList[server['EntryCountry']]
				self.serverNameShort = server['EntryCountry']
			else:
				self.serverNameLong = self.serverNameShort = server['Name']

			if not self.serverNameShort in self.serverList:
				self.serverList[self.serverNameShort] = {'serverList': {}}

			self.serverList[self.serverNameShort]['serverList'][server['Name']] = {
				'id': server['ID'], 
				'load': server['Load'], 
				'score': server['Score'], 
				'domain': server['Domain'], 
				'tier': server['Tier'], 
				'features': server['Features'],
				'servers': server['Servers'],
			}
		self.saveCountryList()
		#print(json.dumps(self.serverList, indent=2))

	#methods saves one country per json file
	def saveCountryList(self):
		if not self.folderManager.returnFolderExist(self.folderName):
			self.folderManager.createFolder(self.folderName)
		for k, v in self.serverList.items():
			if not self.fileManager.returnFileExist(self.folderName, k, 'json'):
				self.fileManager.createFile(self.folderName, k, 'json', json.dumps(v, indent=2))
			else:
				self.fileManager.editFile(self.folderName, k, 'json', json.dumps(v, indent=2))
			
			