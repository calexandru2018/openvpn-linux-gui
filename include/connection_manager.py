import subprocess, requests, re, os, signal, json, pprint, shutil, time
from include.user_manager import UserManager
from include.file_manager import FileManager
from include.folder_manager import FolderManager
from include.server_manager import ServerManager
class ConnectionManager():
	def __init__(self, rootDir, user_man_folder_name, server_man_folder_name):
		#print("\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n\t! In connection manager !\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		self.rootDir = rootDir
		self.user_man_folder_name = user_man_folder_name
		self.server_man_folder_name = server_man_folder_name
		self.user_manager = UserManager(self.rootDir, self.user_man_folder_name)
		self.file_manager = FileManager(self.rootDir)
		self.server_manager = ServerManager(self.rootDir, self.server_man_folder_name)
		self.fileType = "json"
		self.platform = "linux"
		self.ovpn_file = ("server_conf", "ovpn")
		self.ipDyndnsCheckUrl = "http://checkip.dyndns.org"
		self.ipProtonCheckUrl = "https://api.protonmail.ch/vpn/location"
		self.actual_ip = ""
		self.new_ip = ""
		self.protonDNS = "\n#Generated by GUI for ProtonVPN\nnameserver 10.8.8.1"
		self.on_boot_process_name = "openvpn-client@"+self.ovpn_file[0] 

	# modify DNS: modify_dns()
	def modify_dns(self, restore_original_dns=False):
		resolv_conf_path = False
		for root, dirs, files in os.walk("/etc/"):
			if "resolv.conf" in files:
				resolv_conf_path = os.path.join(root, "resolv.conf")

		if(resolv_conf_path):
			print("Modifying dns...")
			resolv_conf_backup = self.rootDir + "/" + self.user_man_folder_name + "/" + "resolv.conf_backup"
			if not restore_original_dns:
				if shutil.copy(resolv_conf_path, resolv_conf_backup):
					cmd = "cat > /etc/resolv.conf <<EOF "+self.protonDNS+"\nEOF"
					try:
						subprocess.run(["sudo", "bash", "-c", cmd])
						print("Created")
						return True
					except:
						print("Unable to create")
						return False
				else:
					print("Unable to update")
					return False
			else:
				try:
					with open(resolv_conf_backup) as f:
						content = f.read()
						cmd = "cat > /etc/resolv.conf <<EOF \n"+content+"\nEOF"
						subprocess.run(["sudo", "bash", "-c", cmd])
						return True
				except:
					print("Unable to restore to original")
		else:
			print("There is no such file")
			return False

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

	def initialize_user_profile(self):
		self.user_manager.create_user_credentials()
		self.user_manager.create_server_conf()
	
	def edit_user_profile(self):
		self.user_manager.ask_what_to_edit()

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

		decodedString = self.cmd_command(["which", "openvpn"])
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
		open_vpn_process = self.cmd_command(["pgrep", "openvpn"])
		#print("Is OpenVPN running: ", open_vpn_process)
		if open_vpn_process:
			return True
		return False

	def check_python_version(self):
		pythonVersion = self.cmd_command(["python", "--version"])
		if pythonVersion and pythonVersion.split(' ')[1] > '3.3':
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
		
		if self.modify_dns():
			var = subprocess.Popen(["sudo", "openvpn", "--daemon", "--config", config_path, "--auth-user-pass", credentials_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			var.wait()
			self.ip_swap("You are now connected.")
			# use sudo systemctl enable openvpn-client@server.service; server is the filename and it should en in .conf

	# disconnect from open_vpn: openvpn_disconnect()
	def openvpn_disconnect(self):
		getPID = False
		command_list = [["pgrep", "openvpn"], ["pid", "openvpn"]]

		try:
			for command in command_list:
				getPID = self.cmd_command(command)
				if getPID:
					# print("FOUND:____", getPID)
					break
		except:
			#print("Unable to find PID")
			return False	
		
		if getPID:
			self.new_ip = self.get_ip()
			if self.modify_dns(restore_original_dns=True):
				var = subprocess.Popen(["sudo", "kill", "-9", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
				#var = subprocess.Popen(["sudo", "kill", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				var.wait()
				self.ip_swap("You are now disconnected.")
		else:
			print("Unable to disconnect, no OpenVPN process was found.")
			return False

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

	def cmd_command(self, *args, return_output=True, as_sudo=False):
		# try:
		if(not return_output and subprocess.run(args[0], stdout=subprocess.PIPE)):
			return True
		else:
			try:
				x = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				return self.decodeToASCII(x.stdout).strip()
			except:
				return False


	def find(self, path, file):
		for root, dirs, files in os.walk(path):
			if file in files:
				#print(file, os.path.join(root, file))
				return True
		return False

	# Optimize when disconnecting, check for openvpn pid
	def ip_swap(self, message):
		time.sleep(2)
		if self.is_internet_working_normally() and (self.actual_ip != self.new_ip):
			self.actual_ip = self.new_ip
			self.new_ip = 0
			print(message)
			FolderManager(self.rootDir).delete_folder_recursive(self.server_manager.folderName)
		else:
			print("An error occurred.")

	def cache_servers(self):
		self.server_manager.collectServerList()

	def openvpn_service_manager(self, action):
		# check first if servers are cached!
		if action == "enable":
			if self.generate_ovpn_for_boot():
				success_msg = "\"Launch on boot\" service enabled."
				fail_msg = "Cant enable \"launch on boot\" service."
		elif action == "disable":
			success_msg = "\"Launch on boot\" service is disabled."
			fail_msg = "Cant disable service \"launch on boot\"."
		elif action == "restart":
			success_msg = "\"Launch on boot\" service restarted."
			fail_msg = "Cant restart \"launch on boot\" service."

		print("systemctl ",action ,self.on_boot_process_name)
		try:
			subprocess.run(["systemctl", action, self.on_boot_process_name])
			FolderManager(self.rootDir).delete_folder_recursive(self.server_manager.folderName)
			print("\n"+success_msg+"\n")
		except:
			print("\n"+fail_msg+"\n")

	def restart_network_manager(self):
		print("systemctl restart", "NetworkManager")
		try:
			subprocess.run(["systemctl", "restart", "NetworkManager"])
			print("\nRestarted network manager\n")
		except:
			print("Cant restart network manager")

	def generate_ovpn_for_boot(self):
		country = input("Which country to connect to: ")
		path = self.rootDir+"/"+"servers_in_cache/"+country.upper() + "."+ self.fileType
			
		with open(path) as file:
			data = json.load(file)

		connectInfo = self.auto_select_optimal_server(data)
		user_selected_protocol = json.loads(self.user_manager.read_user_data())

		url = "https://api.protonmail.ch/vpn/config?Platform=" + self.platform + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_selected_protocol['protocol']
		server_req = requests.get(url, headers={"x-pm-appversion": "Other", "x-pm-apiversion": "3", "Accept": "application/vnd.protonmail.v1+json"})
		original_req = server_req.text
		start_index = original_req.find("auth-user-pass")
		modified_request = original_req[:start_index+14] + " /opt/protonvpn-gui-linux/.user_credentials" + original_req[start_index+14:]
		print(original_req, modified_request)
		resolv_conf_path = False
		try:
			append_to_file = "cat > /etc/openvpn/client/"+self.ovpn_file[0]+".conf <<EOF "+modified_request+"\nEOF"
			subprocess.run(["sudo", "bash", "-c", append_to_file])
			print("Created new file in /openvpn/client/")
		except:
			print("Unable to create")

		for root, dirs, files in os.walk("/opt/"):
			if ".user_credentials" in dirs:
				resolv_conf_path = os.path.join(root, ".user_credentials")
		if(not resolv_conf_path):
			self.copy_credentials()
			return True
		else:
			return False

	def copy_credentials(self):
		cmds = ["mkdir /opt/protonvpn-gui-linux/", "cp " + self.rootDir + "/" + self.user_man_folder_name + "/.user_credentials /opt/protonvpn-gui-linux/"]
		try:
			if(not os.path.isdir("/opt/protonvpn-gui-linux/")):
				for cmd in cmds:
					subprocess.run(["sudo", "bash", "-c", cmd])
			else:
				subprocess.run(["sudo", "bash", "-c", cmds[1]])
			print("Copied credentials")
			return True
		except:
				print("Unable to copy credentials")
				return False

	
	# install update_resolv_conf: install_update_resolv_conf()

	# manage IPV6: manage_ipv6()
	#def manage_ipv6(self):

