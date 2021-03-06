import subprocess, requests, re, os, json, pprint, shutil, time

from include.user_manager import UserManager
from include.server_manager import ServerManager

# Helper methods and constants 
from include.utils.common_methods import (
	walk_to_file, create_file, delete_file, delete_folder_recursive,
	cmd_command, edit_file
)
from include.utils.constants import (
	USER_CRED_FILE, USER_PREF_FILE, OVPN_FILE, CACHE_FOLDER, RESOLV_BACKUP_FILE, IPV6_BACKUP_FILE, SERVER_FILE_TYPE, 
	OS_PLATFORM, USER_FOLDER, PROTON_HEADERS, PROJECT_NAME, PROTON_DNS, ON_BOOT_PROCESS_NAME, LOG_FILE, OVPN_LOG_FILE
)
from include.utils.connection_manager_helper import(
	generate_ovpn_file, generate_ovpn_for_boot, 
	manage_ipv6, get_ip_info, get_fastest_server, req_for_ovpn_file, manage_dns, manage_killswitch
)

from include.logger import log

class ConnectionManager():
	def __init__(self):
		self.server_manager = ServerManager()
		self.user_manager = UserManager()

	#functions below do not belong to connecton manager
	def initialize_user_profile(self):
		self.user_manager.create_user_credentials_file()
		self.user_manager.create_user_pref_file()
	
	def edit_user_profile(self):
		if self.user_manager.ask_what_to_edit():
			print("Data updated successfully")
	#the above two methods must be moved elsewhere

	def start_on_boot_manager(self, action):
		enabled_on_boot = True
		#load user preferences
		try:
			user_pref = self.user_manager.read_user_data()
		except:
			print("Profile was not initialized.")
			log.warning("User profile was not initialized.")
			return False

		if action == "enable":
			success_msg = "\"Launch on boot\" service enabled."
			fail_msg = "Cant enable \"launch on boot\" service."

			self.server_manager.cache_servers()
			server_collection = []

			user_inp_country = input("Which country do you want to start on boot ? ").strip().upper()
			server_list_file = user_inp_country+SERVER_FILE_TYPE

			#load country configurations
			try:
				with open(os.path.join(CACHE_FOLDER, server_list_file)) as file:
					server_list = json.load(file)
			except TypeError:
				print("Servers are not cached.")
				log.warning("Servers are not cached.") 
				return False

			print("Server name|\tServer Load|\tFeatures|\tTier")
			for server in server_list['serverList']:
				if server_list['serverList'][server]['tier'] <= user_pref['tier']:
					server_collection.append(server_list['serverList'][server])
					print(
						server_list['serverList'][server]['name']+"|\t\t\t"+str(server_list['serverList'][server]['load'])+"|\t"+
						str(server_list['serverList'][server]['features'])+"|\t\t"+str(server_list['serverList'][server]['tier'])
					)
			
			if len(server_collection) == 0:
				print("No servers were found")
				return False

			user_selected_server = int(input("Which server to connecto on boot: "))
			selected_server = [server for server in server_collection if str(user_selected_server) in server['name']][0]
			
			user_pref['on_boot_server_id'] = selected_server['id']
			user_pref['on_boot_server_name'] = selected_server['name']
			user_pref['on_boot_protocol'] = user_pref['protocol']
			
			server_req = req_for_ovpn_file(selected_server['id'], user_pref['protocol'])

			if not server_req:
				return False

			if not generate_ovpn_for_boot(server_req):
				return False
		elif action == "kill":
			openvpn_PID = self.check_for_running_ovpn_process()
			if not openvpn_PID:
				print("Not PID was found")
				log.debug("Attempted to kill \"openvpn start on boot\" process, none found.")
				return False

			output = subprocess.run(["sudo","kill", "-9", openvpn_PID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
			if output.returncode != 0:
				print(f"Unable to kill PID {openvpn_PID}.")
				log.critical(f"Unable to disconnecto from VPN, \"{output}\"")
				return False

			self.restart_network_manager()
			return True
		elif action == "disable":
			success_msg = "\"Launch on boot\" service is disabled."
			fail_msg = "Cant disable service \"launch on boot\"."
			enabled_on_boot = False
			#here it should kill all openvpn processes and disable service daemon
		elif action == "restart":
			success_msg = "\"Launch on boot\" service was restarted."
			fail_msg = "Cant restart service \"launch on boot\"."

		try:
			output = subprocess.run(["sudo", "systemctl", action, ON_BOOT_PROCESS_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			log.debug(f"Start on boot log: {output}")
		except:
			print("\n"+fail_msg+"\n")
			log.critical("Something went wrong, could not enable \"start on boot\"")
			return False

		if not delete_folder_recursive(CACHE_FOLDER):
			log.debug("Unable to delete cache folder recursively.")

		print("\n"+success_msg+"\n")
		user_pref['on_boot_enabled'] = enabled_on_boot

		if not edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False):
			log.debug("Unable to save on boot preferences.")

		log.info(f"Start on boot created: \"{output.stdout.decode()}\"")

	def fastest_country(self):
		if self.check_for_running_ovpn_process():
			print("VPN already running.")
			return False

		server_feature_filter = [1, 2]
		server_collection = []
		self.server_manager.cache_servers()

		country = input("Which country to connect to: ").strip().upper()
		file = country+SERVER_FILE_TYPE

		#load country configurations
		try:
			with open(os.path.join(CACHE_FOLDER, file)) as file:
				server_list = json.load(file)
		except TypeError:
			print("Servers are not cached.")
			log.warning("Servers are not cached.") 
			return False

		#load user preferences
		try:
			user_pref = self.user_manager.read_user_data()
		except:
			print("Profile was not initialized.")
			log.warning("User profile was not initialized.")
			return False

		#filter by features and tier
		for server in server_list['serverList']:
			if server_list['serverList'][server]['features'] not in server_feature_filter and server_list['serverList'][server]['tier'] <= user_pref['tier']:
				server_collection.append(server_list['serverList'][server])

		if not len(server_collection):
			print("Nothing")
			return False
		
		server_id, server_score, server_name, server_load = get_fastest_server(server_collection)
		user_pref['last_conn_server_id'] = server_id
		user_pref['last_conn_sever_name'] = server_name
		user_pref['last_conn_sever_protocol'] = user_pref['protocol']

		server_req = req_for_ovpn_file(server_id, user_pref['protocol'])

		if not server_req:
			return False

		if not generate_ovpn_file(server_req):
			return False

		if not self.openvpn_connect(protocol=user_pref['protocol']):
			return False
		
		if not edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False):
			log.debug("Did not manage to save last connection preferences.")

		log.info(f"Updated user last connection data: \"{user_pref}\"")

	#to-do. Should filter all servers by the specified feature and then select with the best score.
	def fastest_feature(self, feature):
		print("Feature", feature)
	
	def connect_to_random(self):
		print("Connect to random")

	def openvpn_connect(self, protocol=False):
		openvpn_PID = self.check_for_running_ovpn_process()
		pre_vpn_conn_ip = False
		port_types = {"udp": 1194, "tcp": 443}

		if openvpn_PID:
			print("Unable to connect, a OpenVPN process is already running.")
			log.info("Unable to connect, a OpenVPN process is already running.")
			return False

		try:
			pre_vpn_conn_ip, pre_vpn_conn_isp = get_ip_info()
		except:
			pre_vpn_conn_ip = False
			pre_vpn_conn_isp = False

		log.info(f"Tested for internet connection: \"{pre_vpn_conn_ip}\"")

		if not pre_vpn_conn_ip:
			print("There is no internet connection.")
			log.warning("Unable to connect, check your internet connection.")
		
		print("Connecting to vpn server...")

		if not protocol:
			protocol = "udp"

		# Needs to be worked on, new way to connect to VPN, might help with killswitch
		with open(OVPN_LOG_FILE, "w+") as log_file:
			subprocess.Popen(
				[	"sudo",
					"openvpn",
					"--config", OVPN_FILE,
					"--auth-user-pass", USER_CRED_FILE
				],
				stdout=log_file, stderr=log_file
			)

		with open(OVPN_LOG_FILE, "r") as log_file:
			while True:
				content = log_file.read()
				log_file.seek(0)
				if "Initialization Sequence Completed" in content:
					print("VPN established")
					#change DNS
					dns_dhcp_regex = re.compile(
						r"(dhcp-option DNS )"
						r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
					)
					dns_dhcp = dns_dhcp_regex.search(content)
					log.debug(f"DNS___RESULT: {dns_dhcp}")
					if dns_dhcp:
						dns_server = dns_dhcp.group(2)
						manage_dns(action_type="custom", dns_addr=dns_server)
					else:
						print("Could not apply custom DNS.")
						log.critical(f"Could not apply custom DNS: {dns_dhcp}")

					if not manage_ipv6(action_type="disable"):
						return False
					# if not manage_killswitch(action_type="enable", protocol=protocol, port=port_types[protocol]):
					# 	return False
					# compare old IP with new IP, if they are different the connection has succeded
					
					log.debug("Connected to the VPN.")
					return True
				elif "AUTH_FAILED" in content:
					print("Authentication failed")
					break

	def openvpn_disconnect(self):
		openvpn_PID = self.check_for_running_ovpn_process()
		is_connected = False
		
		print("Disconnecting from vpn server...")
		log.info(f"PID is: {'NONE' if not openvpn_PID else openvpn_PID}")

		if not openvpn_PID:
			print("Unable to disconnect, no OpenVPN process was found.")
			log.warning("Could not find any OpenVPN processes.")
			return False

		try:
			is_connected = get_ip_info()
		except:
			is_connected = False
		
		log.info(f"Tested for internet connection: \"{is_connected}\"")

		if not manage_dns(action_type="restore"):
			log.critical("Unable to restore DNS prior to disconnecting from VPN, restarting NetworkManager might be needed.")
			
		if not manage_ipv6(action_type="restore"):
			log.warning("Unable to enable IPV6 prior to disconnecting from VPN.")

		# if not manage_killswitch(action_type="restore"):
		# 	return False

		output = subprocess.run(["sudo","kill", "-9", openvpn_PID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
		if output.returncode != 0:
			print("Unable to disconnecto from VPN.")
			log.critical(f"Unable to disconnecto from VPN, \"{output}\"")
			return False

		log.info("Disconnected from VPN.")
		print("You are disconnected from VPN.")
		return True

	def restart_network_manager(self):
		try:
			output = subprocess.run(["systemctl", "restart", "NetworkManager"], stdout=subprocess.PIPE)
			print("\nRestarted network manager\n")
			log.info(f"Sucessfully restarted Network Manager: \"{output.stdout.decode()}\"")
		except:
			log.warning(f"Unable to restart Network Manager.")
			print("Cant restart network manager")

	def is_vpn_running(self):
		openvpn_PID = self.check_for_running_ovpn_process()

		cmd = "cat /etc/resolv.conf"
		res = subprocess.run(["sudo", "bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		# log.info(f"PID is: {'NONE' if not openvpn_PID else openvpn_PID}")

		if openvpn_PID and (res.returncode == 0 and ("10.8.8.1" in res.stdout.decode() or "10.7.7.1" in res.stdout.decode())):
			print("VPN is running with custom DNS.")
			log.info(f"VPN is running\nOVPN PID:{openvpn_PID}\nDNF conf:\n{res.stdout.decode()}")
			return True
		elif openvpn_PID and not (res.returncode == 0 and ("10.8.8.1" in res.stdout.decode() or "10.7.7.1" in res.stdout.decode())):
			print("VPN is running, but there might be DNS leaks. Try modifying your DNS configurations.")
			log.warning(f"Resolv conf has original values, custom ProtonVPN DNS configuration not found: {res.stdout.decode()}")
			return True
		else:
			print("VPN is not running.")
			log.info("Could not find any OpenVPN processes.")
			return False

	def check_for_running_ovpn_process(self):
		openvpn_PID = False
		command_list = [["pgrep", "openvpn"], ["pid", "openvpn"]]
		#no need to try, since cmd_command already does that
		try:
			for command in command_list:
				return_code, openvpn_PID = cmd_command(command)
				if openvpn_PID:
					return openvpn_PID
		except:
			log.warning(f"Could not find any openvpn processes running.")
			return openvpn_PID

	
	def test(self):
		print("Test")