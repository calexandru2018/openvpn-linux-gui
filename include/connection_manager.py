import subprocess, requests, re, os, signal, json, pprint
from include.user_manager import UserManager
from include.server_manager import ServerManger
from include.file_manager import FileManager

class ConnectionManager():
	def __init__(self, rootDir):
		#print("\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n\t! In connection manager !\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		self.rootDir = rootDir
		self.user = UserManager(self.rootDir)
		self.server = ServerManger(self.rootDir)
		self.file = FileManager(self.rootDir)
		self.ipDyndnsCheckUrl = "http://checkip.dyndns.org"
		self.ipProtonCheckUrl = "https://api.protonmail.ch/vpn/location"

	def generate_ovpn_file(self, country_to_check):
		highestScore = 0
		connectToID = ''
		fileName = country_to_check.upper() + ".json"
		#if self.server.filter_servers_country(string):
		#serverList = self.file.readFile('servers_in_cache', country_to_check.upper(), 'json')
		try:
			with open(self.rootDir+"/"+"servers_in_cache/"+fileName) as file:
				data = json.load(file)
				print(data)
				if(data):
					for server in data['serverList']:
						#print(data['serverList'][server]['score'],'SERVER_:_______')
						if data['serverList'][server]['score'] >= highestScore:
							highestScore = data['serverList'][server]['score']
							connectToID = data['serverList'][server]['id']
					connectInfo = (connectToID, highestScore)
					print(connectInfo)
					url = "https://api.protonmail.ch/vpn/config?Platform=linux&LogicalID="+connectInfo[0]+"&Protocol=udp"
					print(url)
					serverReq = requests.get(url, headers={'User-Agent': 'Custom'})
					if self.file.returnFileExist("protonvpn_conf", "server", "ovpn"):
						self.file.deleteFile("protonvpn_conf", "server", "ovpn")
					if self.file.createFile("protonvpn_conf", "server", "ovpn", serverReq.text):
						print("information saved")
						return True
		except FileNotFoundError:
			print("There is no such country")
		
	def check_requirments(self):
		allReqCheck = 6
		checker = {
			'check_python_version': {'name': 'Python Version is above 3.3', 'return': self.check_python_version()},
			'is_internet_working_normally': {'name': 'Your internet is working normally', 'return':self.is_internet_working_normally()},
			'is_profile_initialized': {'name': 'Your profile is initialized', 'return': self.check_if_profile_initialized(requirments_check=True)},
			'is_openvpn_installed': {'name': 'OpenVPN is installed', 'return':self.is_openvpn_installed()}, 
			'is_open_resolv_installed': {'name': 'Open Resolv installed', 'return': self.is_open_resolv_installed('/etc/', 'resolv.conf')},
			'is_update_resolv_conf_installed': {'name': 'Update resolv is installed', 'return': self.update_resolv_conf_installed('/etc/openvpn/', 'update-resolv-conf')}
		}
		for check in checker:
			if not checker[check]['return']:
				allReqCheck -= allReqCheck
			print(f"{checker[check]['name']}: {checker[check]['return']}")
		return allReqCheck == 6

	# check if profile was created/initialized: check_if_profile_initialized()
	def check_if_profile_initialized(self, requirments_check=False):
		'''Checks if user profile is configured/intialized.

		Returns:
		------
		Bool:
			1 - Returns True if user already is configured/intialized.
			2 - Returns True if no user was found and a new one was configured/initialized.
			3 - Returns False if it was unable to configure/initialize a new user. 
		'''
		if self.user.checkUserExists():
			#print("User exists")
			return True
		else:
			if(requirments_check == False):
				userChoice = input("User was not created, would you like to create it now ? [y/n]: ")
				if(userChoice[0].lower() == 'y'):
					if self.user.createUser():
						#print("User created succesfully!")
						return True
					#print("Unable to create user")
					return False
			else:
				return False
 
 	# check for ip: check_ip()
	def check_ip(self):
		'''Gets the host IP from two different sources and compares them.
		
		Returns:
		-------
		Bool:
			True if the IP's match, False otherwise.
		'''
		dyndnsRequest = requests.get(self.ipDyndnsCheckUrl)
		dyndnsIp = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", dyndnsRequest.text)[0].strip()
		protonRequest = requests.get(self.ipProtonCheckUrl, headers={'User-Agent': 'Custom'}).json()
		if dyndnsIp == protonRequest['IP']:
			#print("Internet is OK and your IP is:", dyndnsIp)
			return True
		return False

	# check if there is internet connection: is_internet_working_normally()
	def is_internet_working_normally(self):
		'''Checks if there is internet connection, by getting the IP.
		
		Returns:
		-------
		Bool:
			True if ther is internet connection, False otherwise.
		'''
		if self.check_ip():
			return True
		return False

	# check if openVpn is installed is_openvpn_installed()
	def is_openvpn_installed(self):
		'''Checks if OpenVPN is installed.

		Returns:
		-------
		Bool:
			Returns True if OpenVPN is found installed, False otherwise.
		'''

		decodedString = self.cmdCommand(["which", "openvpn"])
		if decodedString:
			#print("Is OpenVPN installed: ", decodedString)
			return True
		return False

	def check_if_openvpn_is_currently_running(self):
		'''Checks if OpenVPN is running.

		Returns
		-------
		Bool:
			True if PID is found, False otherwise.
		'''
		open_vpn_process = self.cmdCommand(["pgrep", "openvpn"])
		#print("Is OpenVPN running: ", open_vpn_process)
		if open_vpn_process:
			return True
		return False

	def check_python_version(self):
		pythonVersion = self.cmdCommand(["python", "--version"])
		if pythonVersion.split(' ')[1] > '3.3':
			#print("Your Python version: ", pythonVersion)
			return True
		return False

	# check if openresolv is installed: is_open_resolv_installed()
	def is_open_resolv_installed(self, path, fileName):
		if self.find(path, fileName):
			return True
		return False
	
	# check for update_resolv_conf()
	def update_resolv_conf_installed(self, path, fileName):
		if self.find(path, fileName):
			return True
		return False

	# connect to open_vpn: openvpn_connect()
	def openvpn_connect(self):
		path = self.rootDir+"/"+"protonvpn_conf/server.ovpn" 
		with open(self.rootDir+"/"+"protonvpn_conf/proton_ovpn_credentials.json") as file:
			data = json.load(file)

		userdata = data['username'] + "\n" + data['password']
		print(userdata)
		var = subprocess.Popen(["sudo", "openvpn", "--daemon", "--config", path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		var.wait()
		# use sudo systemctl enable openvpn-client@server.service; server is the filename and it should en in .conf

	# disconnect from open_vpn: openvpn_disconnect()
	def openvpn_disconnect(self):
		getPID = self.cmdCommand(["pgrep", "openvpn"])
		var = subprocess.Popen(["sudo", "kill", "-9", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		var.wait()

	# install update_resolv_conf: install_update_resolv_conf()

	# manage IPV6: manage_ipv6()

	# modify DNS: modify_dns() - NOT PRIO

	# initialize CLI: init_cli()

	#check requirments: check_requirements()
		# check if openvpn is installed - done
		# check if python/version is installed - done
		# check for sysctl (identify why ?)
		# check for sha512_sum - not needed
		# check if update-resolv-conf is installed

	# Helper methods
	def decodeToASCII(self, byteValue):
		if byteValue:
			return byteValue.decode('ascii')
		return False

	def cmdCommand(self, *args):
		try:
			return self.decodeToASCII(subprocess.Popen(args[0], stdout=subprocess.PIPE).communicate()[0]).strip()
		except:
			return False

	def find(self, path, file):
		for root, dirs, files in os.walk(path):
			if file in files:
				#print(file, os.path.join(root, file))
				return True
		return False
