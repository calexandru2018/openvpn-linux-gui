import subprocess, requests, re, os, signal, json, pprint, shutil, time, netifaces

from .user_manager import UserManager
from .server_manager import ServerManager

# Helper methods and constants 
from .static.utils import (
	returnFileExist, createFile, readFile, deleteFile, delete_folder_recursive, walk_to_file,
	cmd_command, auto_select_optimal_server, decodeToASCII
)
from .static.constants import (
	USER_FOLDER, USER_CRED_FILE, OVPN_FILE, CACHE_FOLDER, RESOLV_BACKUP_FILE, IPV6_BACKUP_FILE, SERVER_FILE_TYPE, 
	OS_PLATFORM, DYNDNS_CHECK_URL, PROTON_CHECK_URL, PROTON_HEADERS, PROJECT_NAME,
	PROTON_DNS, ON_BOOT_PROCESS_NAME
)
class ConnectionManager():
	def __init__(self, rootDir):
		#print("\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n\t! In connection manager !\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		self.rootDir = rootDir
		self.server_manager = ServerManager(self.rootDir)
		self.user_manager = UserManager(self.rootDir)
		self.actual_ip = False
		self.new_ip = False

	# modify DNS: modify_dns()
	def modify_dns(self, restore_original_dns=False):
		resolv_conf_path = walk_to_file("/etc/", "resolv.conf", is_return_bool=False)
		
		if(resolv_conf_path):
			print("Modifying dns...")
			resolv_conf_backup = self.rootDir + "/" + USER_FOLDER + "/" + RESOLV_BACKUP_FILE
			if not restore_original_dns:
				if shutil.copy(resolv_conf_path, resolv_conf_backup):
					cmd = "cat > /etc/resolv.conf <<EOF "+PROTON_DNS+"\nEOF"
					try:
						subprocess.run(["sudo", "bash", "-c", cmd])
						print("DNS updated with new configurations.")
						return True
					except:
						print("unable to update DNS configurations")
						return False
				else:
					print("Unable to back DNS configurations.")
					return False
			else:
				try:
					with open(resolv_conf_backup) as f:
						content = f.read()
						cmd = "cat > /etc/resolv.conf <<EOF \n"+content+"\nEOF"
						subprocess.run(["sudo", "bash", "-c", cmd])
						print("Restored to original DNS configurations.")
						return True
				except:
					print("Unable to restore original DNS configurations, try restarting the Network Manager.")
		else:
			print("The \"resolv.conf\" file was not found on your system.")
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
		country = input("Which country to connect to: ")
		path = self.rootDir+"/" + CACHE_FOLDER + "/"
		file = country.upper() + SERVER_FILE_TYPE

		try:
			data = json.loads(readFile(path, file))
		except TypeError:
			print("Servers are not cached.") 
			return False

		try:
			user_selected_protocol = json.loads(self.user_manager.read_user_data())
		except TypeError:
			print("Profile was not initialized.")
			return False

		connectInfo = auto_select_optimal_server(data)
		url = "https://api.protonmail.ch/vpn/config?Platform=" + OS_PLATFORM + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_selected_protocol['protocol']

		serverReq = requests.get(url, headers=(PROTON_HEADERS))

		if walk_to_file(self.rootDir+"/"+USER_FOLDER, OVPN_FILE):
			deleteFile(self.rootDir+"/"+USER_FOLDER+"/", OVPN_FILE)
		if createFile(self.rootDir+"/"+USER_FOLDER+"/"+OVPN_FILE, serverReq.text):
			print("An ovpn file has bee created, try to establish a connection now.")
			return True
		
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
		if self.user_manager.ask_what_to_edit():
			print("Data updated successfully")

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
		dyndnsRequest = requests.get(DYNDNS_CHECK_URL)
		dyndnsIp = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", dyndnsRequest.text)[0].strip()

		protonRequest = requests.get(PROTON_CHECK_URL, headers=(PROTON_HEADERS)).json()

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
		decodedString = cmd_command(["which", "openvpn"])
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
		open_vpn_process = cmd_command(["pgrep", "openvpn"])
		#print("Is OpenVPN running: ", open_vpn_process)
		if open_vpn_process:
			return True
		return False

	def check_python_version(self):
		pythonVersion = cmd_command(["python", "--version"])
		if pythonVersion and pythonVersion.split(' ')[1] > '3.3':
			return True
		return False

	# check if openresolv is installed: is_open_resolv_installed()
	def is_open_resolv_installed(self, path, fileName):
		return walk_to_file(path, fileName)
	
	# check for update_resolv_conf()
	def is_update_resolv_conf_installed(self, path, fileName):
		return walk_to_file(path, fileName)

	# connect to open_vpn: openvpn_connect()
	def openvpn_connect(self):
		config_path = self.rootDir + "/" + USER_FOLDER + "/" + OVPN_FILE
		credentials_path = self.rootDir + "/" + USER_FOLDER + "/" + USER_CRED_FILE
		
		print("Connecting to vpn server...")
		if self.get_ip():
			if self.modify_dns() and self.manage_ipv6(disable_ipv6=True):
				var = subprocess.Popen(["sudo", "openvpn", "--daemon", "--config", config_path, "--auth-user-pass", credentials_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				var.wait()
				self.ip_swap("connect")
		else:
			print("There is no internet connection.")

	# disconnect from open_vpn: openvpn_disconnect()
	def openvpn_disconnect(self):
		getPID = False
		command_list = [["pgrep", "openvpn"], ["pid", "openvpn"]]
		try:
			for command in command_list:
				getPID = cmd_command(command)
				if getPID:
					break
		except:
			# print("cant find running openvpn process")
			return False	
		
		print("Disconnecting from vpn server...")
		if getPID:
			self.new_ip = self.get_ip()
			if self.modify_dns(restore_original_dns=True):
				self.manage_ipv6(disable_ipv6=False)
				var = subprocess.Popen(["sudo", "kill", "-9", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
				var.wait()
				self.ip_swap("disconnect")
		else:
			print("Unable to disconnect, no OpenVPN process was found.")
			return False

	# Optimize when disconnecting, check for openvpn pid
	def ip_swap(self, action):
		success_msg = "Connected to vpn server."
		fail_msg = "Unable to connect to vpn server."
		if action == "disconnect":
			success_msg = "Disconnected from vpn server."
			fail_msg = "Unable to disconnected from vpn server."

		time.sleep(4)

		if self.is_internet_working_normally() and (self.actual_ip != self.get_ip()):
			self.actual_ip = self.new_ip
			self.new_ip = False
			print(success_msg)
			delete_folder_recursive(self.rootDir+"/"+CACHE_FOLDER)
		else:
			print(fail_msg)

	def cache_servers(self):
		self.server_manager.collectServerList()

	def openvpn_service_manager(self, action):
		# check first if servers are cached!
		servers_are_cached = False
		if action == "enable":
			if self.generate_ovpn_for_boot():
				success_msg = "\"Launch on boot\" service enabled."
				fail_msg = "Cant enable \"launch on boot\" service."
				servers_are_cached = True
			else:
				#print("There is no such file")
				return False
		elif action == "disable":
			success_msg = "\"Launch on boot\" service is disabled."
			fail_msg = "Cant disable service \"launch on boot\"."

		#print("systemctl", action, ON_BOOT_PROCESS_NAME)
		if action == "enable" and not servers_are_cached: 
			print("Unable to create service, servers were not cached.")
			return False
		try:
			subprocess.run(["sudo", "systemctl", action, ON_BOOT_PROCESS_NAME])
			delete_folder_recursive(self.rootDir+"/"+CACHE_FOLDER)
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
		path = self.rootDir+"/"+CACHE_FOLDER+"/"+country.upper() + SERVER_FILE_TYPE

		if returnFileExist(path):
			with open(path) as file:
				data = json.load(file)

			connectInfo = auto_select_optimal_server(data)
			user_selected_protocol = json.loads(self.user_manager.read_user_data())

			url = "https://api.protonmail.ch/vpn/config?Platform=" + OS_PLATFORM + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_selected_protocol['protocol']
			server_req = requests.get(url, headers=(PROTON_HEADERS))
			original_req = server_req.text
			start_index = original_req.find("auth-user-pass")
			modified_request = original_req[:start_index+14] + " /opt/" + PROJECT_NAME + "/" + USER_CRED_FILE + original_req[start_index+14:]

			try:
				append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"
				subprocess.run(["sudo", "bash", "-c", append_to_file])
				print("Created new file in /openvpn/client/")
			except:
				print("Unable to create configuration file in /oepnvpn/client")

			if(not walk_to_file("/opt/", USER_CRED_FILE, in_dirs=True)):
				self.copy_credentials()
				return True
			else:
				return False
		else:
			print("There is no such file, maybe servers are not cached ?")
			return False

	def copy_credentials(self):
		cmds = ["mkdir /opt/"+PROJECT_NAME+"/", "cp " + self.rootDir + "/" + USER_FOLDER + "/"+USER_CRED_FILE+" /opt/"+PROJECT_NAME+"/"]
		try:
			if(not os.path.isdir("/opt/"+PROJECT_NAME+"/")):
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
	def manage_ipv6(self, disable_ipv6):
		ipv6 = False
		netmask = False
		enable_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=1"]
		enable_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=1"]

		if not disable_ipv6:
			with open(self.rootDir + "/" + USER_FOLDER + "/" + IPV6_BACKUP_FILE, "r") as file:
				content = file.read().split()
			enable_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=0"]
			enable_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=0"]
			if cmd_command(enable_default, as_sudo=True) and cmd_command(enable_all, as_sudo=True):
				cmd_command(["ip", "addr", "add", content[1] , "dev", content[0]],  as_sudo=True)
				print("IPV6 Restored and linklocal restored.")
				return True
			print("Did not manage to restore IPV6, needs to be restored manually.")
			return False
		else:
			interfaces = netifaces.interfaces()
			for interface in interfaces:
				confs = netifaces.ifaddresses(interface)
				addrs = confs.get(netifaces.AF_INET6, False)
				if addrs:
					for address in addrs:
						ipv6 = re.match("fe80::[0-9a-z]{4}:[0-9a-z]{4}:[0-9a-z]{4}:[0-9a-z]{4}", address['addr'])
						if ipv6:
							interface_to_save = interface
							netmask = address['netmask'].split("::")[1]
							ipv6 = ipv6.group(0)
							break
			if ipv6 and netmask:
				if returnFileExist(self.rootDir + "/"+ USER_FOLDER + "/" + IPV6_BACKUP_FILE):	
					deleteFile(self.rootDir + "/" + USER_FOLDER + "/", IPV6_BACKUP_FILE)
				with open(self.rootDir + "/" + USER_FOLDER + "/" + IPV6_BACKUP_FILE, "w") as file:
					file.write(interface_to_save + " " + ipv6 + netmask)
					if cmd_command(enable_default, as_sudo=True) and cmd_command(enable_all, as_sudo=True):
						print("IPV6 disabled.")
						return True
			else:
				return False
