import requests, json, os

from include.utils.constants import (CACHE_FOLDER, PATH_TO_CACHE_FOLDER, SERVER_FILE_TYPE, PROTON_SERVERS_URL, PROTON_HEADERS)
from include.utils.methods import(create_file, edit_file, walk_to_file, create_folder, delete_folder_recursive, folder_exist)

class ServerManager():
	def __init__(self, rootDir):
		self.rootDir = rootDir
		self.serverList = {}
		self.country_full_name = ''
		self.country_iso_name = ''
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
		#self.collectServerList()
	
	def collectServerList(self):
		serverReq = requests.get(PROTON_SERVERS_URL, headers=(PROTON_HEADERS)).json()
		for server in serverReq['LogicalServers']:
			if server['EntryCountry'] in self.countryList:
				self.country_full_name = self.countryList[server['EntryCountry']]
				self.country_iso_name = server['EntryCountry']
			else:
				self.country_full_name = self.country_iso_name = server['Name']

			if not self.country_iso_name in self.serverList:
				self.serverList[self.country_iso_name] = {'serverList': {}}

			self.serverList[self.country_iso_name]['serverList'][server['Name']] = {
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
		if not folder_exist(PATH_TO_CACHE_FOLDER):
			create_folder(PATH_TO_CACHE_FOLDER)
		else:
			if delete_folder_recursive(PATH_TO_CACHE_FOLDER):
				create_folder(PATH_TO_CACHE_FOLDER)
			else:
				print("Unable to delete folder ", PATH_TO_CACHE_FOLDER)
				return False

		for country, content in self.serverList.items():
			country_path = os.path.join(PATH_TO_CACHE_FOLDER, country+SERVER_FILE_TYPE)
			if not walk_to_file(PATH_TO_CACHE_FOLDER, country+SERVER_FILE_TYPE):
				create_file(country_path, json.dumps(content, indent=2))
			else:
				edit_file(country_path, json.dumps(content, indent=2))
		print("Servers cached successfully!")

			