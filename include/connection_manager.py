import subprocess, requests, re, os, signal, json, pprint
from include.user_manager import UserManager
from include.file_manager import FileManager
from include.folder_manager import FolderManager
from include.server_manager import ServerManager
class ConnectionManager():
	def __init__(self, rootDir):
		#print("\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n\t! In connection manager !\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		self.rootDir = rootDir
		self.user_manager = UserManager(self.rootDir)
		self.file_manager = FileManager(self.rootDir)
		self.fileType = "json"
		self.platform = "linux"
		self.ovpn_file = ("server_conf", "ovpn")
		self.ipDyndnsCheckUrl = "http://checkip.dyndns.org"
		self.ipProtonCheckUrl = "https://api.protonmail.ch/vpn/location"
		self.actual_ip = ""
		self.new_ip = ""

	def generate_ovpn_file(self):
		'''Generates OVPN files
		
		Tier 0(1) = Free
		Tier 1(2) = Basic
		Tier 2(3) = Plus
		Tier 3(4) = Visionary
		
		Feature 1: Secure Core
		Feature 2: Tor
		Feature 4: P2P
		Feature 8: XOR (not in use)
		Feature 16: IPV6 (not in use)
		'''

		try:
			country = input("Which country to connect to: ")
			path = self.rootDir+"/"+"servers_in_cache/"+country.upper() + "."+ self.fileType
				
			with open(path) as file:
				data = json.load(file)

			connectInfo = self.auto_select_optimal_server(data)
			user_selected_protocol = json.loads(self.user_manager.read_user_data())

			url = "https://api.protonmail.ch/vpn/config?Platform=" + self.platform + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_selected_protocol['protocol']

			serverReq = requests.get(url, headers={'User-Agent': 'Custom'})
			if self.file_manager.returnFileExist("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1]):
				self.file_manager.deleteFile("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1])
			if self.file_manager.createFile("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1], serverReq.text):
				print("An ovpn file has bee created, try to establish a connection now.")
				return True
		except FileNotFoundError:
			print("There is no such country, maybe servers were not cached ?")
		
	def check_requirments(self):
		allReqCheck = 6
		checker = {
			'check_python_version': {'name': 'Python Version is above 3.3', 'return': self.check_python_version()},
			'is_internet_working_normally': {'name': 'Your internet is working normally', 'return':self.is_internet_working_normally()},
			'is_profile_initialized': {'name': 'Your profile is initialized', 'return': self.check_if_profile_initialized(requirments_check=True)},
			'is_openvpn_installed': {'name': 'OpenVPN is installed', 'return':self.is_openvpn_installed()}, 
			'is_open_resolv_installed': {'name': 'Open Resolv installed', 'return': self.is_open_resolv_installed('/etc/', 'resolv.conf')},
			'is_is_update_resolv_conf_installed': {'name': 'Update resolv is installed', 'return': self.is_update_resolv_conf_installed('/etc/openvpn/', 'update-resolv-conf')}
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
		if self.user_manager.check_if_user_exist():
			#print("User exists")
			return True
		else:
			if(requirments_check == False):
				userChoice = input("User was not created, would you like to create it now ? [y/n]: ")
				if(userChoice[0].lower() == 'y'):
					if self.user_manager.create_server_conf() and self.user_manager.create_user_credentials():
						print("User created succesfully!")
						return True
					print("Unable to create user")
					return False
			else:
				return False
 
 	# check for ip: get_ip()
	def get_ip(self):
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
			return protonRequest['IP']
		return False

	# check if there is internet connection: is_internet_working_normally()
	def is_internet_working_normally(self):
		'''Checks if there is internet connection, by getting the IP.
		
		Returns:
		-------
		Bool:
			True if ther is internet connection, False otherwise.
		'''
		if self.get_ip():
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
			return True
		return False

	# check if openresolv is installed: is_open_resolv_installed()
	def is_open_resolv_installed(self, path, fileName):
		if self.find(path, fileName):
			return True
		return False
	
	# check for update_resolv_conf()
	def is_update_resolv_conf_installed(self, path, fileName):
		if self.find(path, fileName):
			return True
		return False

	# connect to open_vpn: openvpn_connect()
	def openvpn_connect(self):
		config_path = self.rootDir+"/"+self.user_manager.folder_name+"/"+self.ovpn_file[0]+"."+self.ovpn_file[1]
		credentials_path = self.rootDir+"/"+self.user_manager.folder_name+"/."+self.user_manager.file_user_credentials_type 
		
		self.new_ip = self.get_ip()
		
		var = subprocess.Popen(["sudo", "openvpn", "--daemon", "--config", config_path, "--auth-user-pass", credentials_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		var.wait()
		self.ip_swap("You are now connected.")
		# use sudo systemctl enable openvpn-client@server.service; server is the filename and it should en in .conf

	# disconnect from open_vpn: openvpn_disconnect()
	def openvpn_disconnect(self):
		getPID = self.cmdCommand(["pgrep", "openvpn"])
		
		self.new_ip = self.get_ip()
		
		var = subprocess.Popen(["sudo", "kill", "-9", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
		#var = subprocess.Popen(["sudo", "kill", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		var.wait()
		
		self.ip_swap("You are now disconnected.")

	# Helper methods
	def auto_select_optimal_server(self, data):
		highestScore = 0
		connectToID = ''
		for server in data['serverList']:
			if (data['serverList'][server]['score'] >= highestScore) and (int(data['serverList'][server]['tier']) == 1):
				highestScore = data['serverList'][server]['score']
				connectToID = data['serverList'][server]['id']
		connectInfo = (connectToID, highestScore)
		return connectInfo

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

	def ip_swap(self, message):
		#time.sleep(25)
		if self.is_internet_working_normally() and (self.actual_ip != self.new_ip):
			self.actual_ip = self.new_ip
			self.new_ip = 0
			print(message)
			FolderManager(self.rootDir).delete_folder_recursive(ServerManager(self.rootDir).folderName)
		else:
			print("An error occurred.")

	def start_on_boot(self):
		# will work specifically on manjaro
		self.generate_ovpn_for_boot()
		# if self.generate_ovpn_for_boot():
		# 	fileName = "openvpn-client@"+self.ovpn_file[0]+".service"
		# 	var = subprocess.Popen(["systemctl", "enable", fileName], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# 	var.wait()

	def generate_ovpn_for_boot(self):
		# try:
		country = input("Which country to connect to: ")
		path = self.rootDir+"/"+"servers_in_cache/"+country.upper() + "."+ self.fileType
			
		with open(path) as file:
			data = json.load(file)

		connectInfo = self.auto_select_optimal_server(data)
		user_selected_protocol = json.loads(self.user_manager.read_user_data())

		url = "https://api.protonmail.ch/vpn/config?Platform=" + self.platform + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_selected_protocol['protocol']

		server_req = requests.get(url, headers={'User-Agent': 'Custom'})

		original_req = server_req.text
		#print(original_req.find("auth-user-pass"))
		modified_request = original_req[:1699] + " /opt/.user_credentials" + original_req[1699:]
		#print(modified_request)
		# WILL ONLY WORK IF THE GENERATED FILS IS WITHIN /OPT/[OPTIONAL NAME]
		newFile = open("/etc/openvpn/client/"+self.ovpn_file[0]+".conf", "w")
		newFile.write(modified_request)

		# except IOError:
		# 	print("Unable to create file", IOError)
		# 	return False
			
		# 	if self.file_manager.returnFileExist("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1]):
		# 		self.file_manager.deleteFile("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1])
		# 	if self.file_manager.createFile("protonvpn_conf", self.ovpn_file[0], self.ovpn_file[1], serverReq.text):
		# 		print("An ovpn file has bee created, try to establish a connection now.")
		# 		return True
		# except FileNotFoundError:
		# 	print("There is no such country, maybe servers were not cached ?")

	# install update_resolv_conf: install_update_resolv_conf()

	# manage IPV6: manage_ipv6()

	# modify DNS: modify_dns() - NOT PRIO

	#check requirments: check_requirements()
		# check if openvpn is installed - done
		# check if python/version is installed - done
		# check for sysctl (identify why ?)
		# check for sha512_sum - not needed
		# check if update-resolv-conf is installed - done
