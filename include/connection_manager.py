import subprocess, requests, re, os, json, pprint, shutil, time, netifaces

from include.user_manager import UserManager
from include.server_manager import ServerManager

# Helper methods and constants 
from include.utils.methods import (
	walk_to_file, create_file, read_file, delete_file, delete_folder_recursive,
	cmd_command, auto_select_optimal_server, get_ip, edit_file
)
from include.utils.constants import (
	USER_CRED_FILE, USER_PREF_FILE, OVPN_FILE, CACHE_FOLDER, RESOLV_BACKUP_FILE, IPV6_BACKUP_FILE, SERVER_FILE_TYPE, 
	OS_PLATFORM, USER_FOLDER, PROTON_HEADERS, PROJECT_NAME, PROTON_DNS, ON_BOOT_PROCESS_NAME
)
class ConnectionManager():
	def __init__(self):
		self.server_manager = ServerManager()
		self.user_manager = UserManager()

	# modify DNS: modify_dns()
	def modify_dns(self, restore_original_dns=False):
		resolv_conf_path = walk_to_file("/etc/", "resolv.conf", is_return_bool=False)
		
		if(resolv_conf_path):
			print("Modifying dns...")
			#resolv_conf_backup = self.rootDir + "/" + USER_FOLDER + "/" + RESOLV_BACKUP_FILE
			if not restore_original_dns:
				#if shutil.copy(resolv_conf_path, resolv_conf_backup):
				if shutil.copy(resolv_conf_path, RESOLV_BACKUP_FILE):
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
					#with open(resolv_conf_backup) as f:
					with open(RESOLV_BACKUP_FILE) as f:
						content = f.read()
						cmd = "cat > /etc/resolv.conf <<EOF \n"+content+"\nEOF"
						subprocess.run(["sudo", "bash", "-c", cmd])
						print("Restored to original DNS configurations.")
						delete_file(RESOLV_BACKUP_FILE)
						return True
				except:
					print("Unable to restore original DNS configurations, try restarting the Network Manager.")
		else:
			print("The \"resolv.conf\" file was not found on your system.")
			return False
		
	# Optimize when disconnecting, check for openvpn pid
	def ip_swap(self, action, actual_IP):
		success_msg = "Connected to vpn server."
		fail_msg = "Unable to connect to vpn server."
		new_IP = False

		if action == "disconnect":
			success_msg = "Disconnected from vpn server."
			fail_msg = "Unable to disconnected from vpn server."
		
		# print("value of actual IP", self.actual_ip)
		try:
			new_IP = get_ip()
		except:
			print("Unable to get new IP")

		if (actual_IP and new_IP) and actual_IP != new_IP:
			print(success_msg)
			delete_folder_recursive(CACHE_FOLDER)
		else:
			print(fail_msg)

	# connect to open_vpn: openvpn_connect()
	def openvpn_connect(self):
		is_connected = False
		
		print("Connecting to vpn server...")
		try:
			is_connected = get_ip()
		except:
			is_connected = False

		if is_connected:
			if self.modify_dns() and self.manage_ipv6(disable_ipv6=True):
				var = subprocess.Popen(["sudo","openvpn", "--daemon", "--config", OVPN_FILE, "--auth-user-pass", USER_CRED_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				var.wait()
				self.ip_swap("connect", is_connected)
		else:
			print("There is no internet connection.")

	# disconnect from open_vpn: openvpn_disconnect()
	def openvpn_disconnect(self):
		getPID = False
		is_connected = False
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
			try:
				is_connected = get_ip()
			except:
				is_connected = False
			if self.modify_dns(restore_original_dns=True):
				self.manage_ipv6(disable_ipv6=False)
				var = subprocess.Popen(["sudo","kill", "-9", getPID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
				var.wait()
				self.ip_swap("disconnect", is_connected)
		else:
			print("Unable to disconnect, no OpenVPN process was found.")
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
		file = country.upper() + SERVER_FILE_TYPE
		try:
			data = json.loads(read_file(CACHE_FOLDER, file))
		except TypeError:
			print("Servers are not cached.") 
			return False

		try:
			user_pref = json.loads(self.user_manager.read_user_data())
		except TypeError:
			print("Profile was not initialized.")
			return False

		connectInfo = auto_select_optimal_server(data, user_pref['tier'])
		# print(json.dumps(connectInfo, indent=3))
		# print(connectInfo)
		user_pref['last_conn_server_id'] = connectInfo[0]
		user_pref['last_conn_sever_name'] = connectInfo[2]
		user_pref['last_conn_sever_protocol'] = user_pref['protocol']
		url = "https://api.protonmail.ch/vpn/config?Platform=" + OS_PLATFORM + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_pref['protocol']

		serverReq = requests.get(url, headers=(PROTON_HEADERS))


		if walk_to_file(USER_FOLDER, OVPN_FILE.split("/")[-1]):
			delete_file(OVPN_FILE)
		if create_file(OVPN_FILE, serverReq.text):
			print("An ovpn file has bee created, try to establish a connection now.")
			edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False)
			return True

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
		elif action == "restart":
			success_msg = "\"Launch on boot\" service was restarted."
			fail_msg = "Cant restart service \"launch on boot\"."

		#print("systemctl", action, ON_BOOT_PROCESS_NAME)
		if action == "enable" and not servers_are_cached: 
			print("Unable to create service, servers were not cached.")
			return False
		try:
			subprocess.run(["sudo", "systemctl", action, ON_BOOT_PROCESS_NAME])
			delete_folder_recursive(CACHE_FOLDER)
			print("\n"+success_msg+"\n")
		except:
			print("\n"+fail_msg+"\n")

	def generate_ovpn_for_boot(self):
		country = input("Which country to connect to: ")
		#path = self.rootDir+"/"+CACHE_FOLDER
		file = country.upper() + SERVER_FILE_TYPE

		if walk_to_file(CACHE_FOLDER, file):
			with open(os.path.join(CACHE_FOLDER, file)) as file:
				data = json.load(file)

			user_pref = json.loads(self.user_manager.read_user_data())
			connectInfo = auto_select_optimal_server(data, user_pref['tier'])

			url = "https://api.protonmail.ch/vpn/config?Platform=" + OS_PLATFORM + "&LogicalID="+connectInfo[0]+"&Protocol=" + user_pref['protocol']
			server_req = requests.get(url, headers=(PROTON_HEADERS))
			original_req = server_req.text
			start_index = original_req.find("auth-user-pass")
			modified_request = original_req[:start_index+14] + " /opt/" + PROJECT_NAME + "/" + OVPN_FILE.split("/")[-1] + original_req[start_index+14:]
			try:
				#append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"
				append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split("/")[-1].split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"
				subprocess.run(["sudo", "bash", "-c", append_to_file])
				print("Created new file in /openvpn/client/")
			except:
				print("Unable to create configuration file in /openvpn/client/")

			if(not walk_to_file("/opt/", USER_CRED_FILE, in_dirs=True)):
				self.copy_credentials()
				return True
			else:
				return False
		else:
			print("There is no such file, maybe servers are not cached ?")
			return False

	# manage IPV6: manage_ipv6()
	def manage_ipv6(self, disable_ipv6):
		ipv6 = False
		netmask = False
		ipv6_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=1"]
		ipv6_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=1"]

		if not disable_ipv6:
			with open(IPV6_BACKUP_FILE, "r") as file:
				content = file.read().split()
			ipv6_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=0"]
			ipv6_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=0"]
			if cmd_command(ipv6_default, as_sudo=True) and cmd_command(ipv6_all, as_sudo=True):
				cmd_command(["ip", "addr", "add", content[1] , "dev", content[0]],  as_sudo=True)
				print("IPV6 Restored and linklocal restored.")
				delete_file(IPV6_BACKUP_FILE)
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
				if walk_to_file(USER_FOLDER, IPV6_BACKUP_FILE.split("/")[-1]):	
					delete_file(IPV6_BACKUP_FILE)
				with open(IPV6_BACKUP_FILE, "w") as file:
					file.write(interface_to_save + " " + ipv6 + netmask)
					if cmd_command(ipv6_default, as_sudo=True) and cmd_command(ipv6_all, as_sudo=True):
						print("IPV6 disabled.")
						return True
			else:
				return False

	def restart_network_manager(self):
		print("systemctl restart", "NetworkManager")
		try:
			subprocess.run(["systemctl", "restart", "NetworkManager"])
			print("\nRestarted network manager\n")
		except:
			print("Cant restart network manager")

	def cache_servers(self):
		self.server_manager.collectServerList()

	def initialize_user_profile(self):
		self.user_manager.create_user_credentials()
		self.user_manager.create_server_conf()
	
	def edit_user_profile(self):
		if self.user_manager.ask_what_to_edit():
			print("Data updated successfully")

	def copy_credentials(self):
		cmds = ["mkdir /opt/"+PROJECT_NAME+"/", "cp " +USER_CRED_FILE+" /opt/"+PROJECT_NAME+"/"]
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
