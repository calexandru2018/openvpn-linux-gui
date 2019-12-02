import subprocess, requests, re, os, json, pprint, shutil, time, netifaces

from include.user_manager import UserManager
from include.server_manager import ServerManager

# Helper methods and constants 
from include.utils.methods import (
	walk_to_file, create_file, delete_file, delete_folder_recursive,
	cmd_command, get_ip, edit_file
)
from include.utils.constants import (
	USER_CRED_FILE, USER_PREF_FILE, OVPN_FILE, CACHE_FOLDER, RESOLV_BACKUP_FILE, IPV6_BACKUP_FILE, SERVER_FILE_TYPE, 
	OS_PLATFORM, USER_FOLDER, PROTON_HEADERS, PROJECT_NAME, PROTON_DNS, ON_BOOT_PROCESS_NAME
)
from include.utils.connection_manager_helper import(
	generate_ovpn_file, generate_ovpn_for_boot, modify_dns, manage_ipv6,
)

from include.logger import log

class ConnectionManager():
	def __init__(self):
		self.server_manager = ServerManager()
		self.user_manager = UserManager()

	#Functions below do not belong to connecton manager
	def initialize_user_profile(self):
		self.user_manager.create_user_credentials_file()
		self.user_manager.create_user_pref_file()
	
	def edit_user_profile(self):
		if self.user_manager.ask_what_to_edit():
			print("Data updated successfully")
	#Above two methods must be moved elsewhere


	def connect_to_optimal_country_server(self):
		self.server_manager.cache_servers()
		if not generate_ovpn_file(self.user_manager.read_user_data()):
			return False
		if not self.openvpn_connect():
			return False

	def connect_to_p2p(self):
		print("P2P")
	
	def connect_to_tor(self):
		print("To TOR")
	
	def connect_to_secure_core(self):
		print("Secure Core")
	
	def connect_to_random(self):
		print("Connect to random")

	# connect to open_vpn: openvpn_connect()
	def openvpn_connect(self):
		openvpn_PID = self.check_for_running_ovpn_process()
		pre_vpn_conn_ip = False

		if openvpn_PID:
			print("Unable to connect, a OpenVPN process is already running.")
			log.info("Unable to connect, a OpenVPN process is already running.")
			return False
		
		print("Connecting to vpn server...")
		try:
			pre_vpn_conn_ip, pre_vpn_conn_isp = get_ip()
		except:
			pre_vpn_conn_ip = False
			pre_vpn_conn_isp = False

		log.info(f"Tested for internet connection: \"{pre_vpn_conn_ip}\"")

		if not pre_vpn_conn_ip:
			print("There is no internet connection.")
			log.warning("Unable to connect, check your internet connection.")
		
		if not modify_dns():
			return False
		
		if not manage_ipv6(disable_ipv6=True):
			return False

		var = subprocess.run(["sudo","openvpn", "--daemon", "--config", OVPN_FILE, "--auth-user-pass", USER_CRED_FILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		if var.returncode != 0:
			print("Unable to connecto to VPN.")
			log.critical(f"Unable to connected to VPN, \"{var}\"")
			return False

		# time.sleep(2)

		# try:
		# 	post_vpn_conn_ip, post_vpn_conn_isp = get_ip()
		# except:
		# 	post_vpn_conn_ip = False
		# 	post_vpn_conn_isp = False

		# print(f"Old IP: {pre_vpn_conn_ip} and old IPS: {pre_vpn_conn_isp}\nNew IP: {post_vpn_conn_ip} and new IPS: {post_vpn_conn_isp}")
		
		log.info("Connected to VPN.")
		print("You are connected to the VPN.")
		return True
		#self.ip_swap("connect", pre_vpn_conn_ip)

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
			is_connected = get_ip()
		except:
			is_connected = False
		
		log.info(f"Tested for internet connection: \"{is_connected}\"")

		if not modify_dns(restore_original_dns=True):
			log.critical("Unable to restore DNS prior to disconnecting from VPN, restarting NetworkManager might be needed.")
			
		if not manage_ipv6(disable_ipv6=False):
			log.warning("Unable to enable IPV6 prior to disconnecting from VPN.")

		var = subprocess.run(["sudo","kill", "-9", openvpn_PID], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# SIGTERM - Terminate opevVPN, ref: https://www.poftut.com/what-is-linux-sigterm-signal-and-difference-with-sigkill/
		if var.returncode != 0:
			print("Unable to disconnecto from VPN.")
			log.critical(f"Unable to disconnecto from VPN, \"{var}\"")
			return False

		log.info("Disconnected from VPN.")
		print("You are disconnected from VPN.")
		return True
		#self.ip_swap("disconnect", is_connected)	

	def start_openvpn_on_boot(self, action):
		# check first if servers are cached!
		servers_are_cached = False
		enabled_on_boot = True
		if action == "enable":
			if not generate_ovpn_for_boot(self.user_manager.read_user_data()):
				return False

			success_msg = "\"Launch on boot\" service enabled."
			fail_msg = "Cant enable \"launch on boot\" service."
			servers_are_cached = True
				
		if action == "enable" and not servers_are_cached: 
			print("Unable to create service, servers were not cached.")
			log.debug("Unable to create service, servers were not cached.")
			return False

		
		if action == "disable":
			success_msg = "\"Launch on boot\" service is disabled."
			fail_msg = "Cant disable service \"launch on boot\"."
			self.openvpn_disconnect()
			enabled_on_boot = False
		elif action == "restart":
			success_msg = "\"Launch on boot\" service was restarted."
			fail_msg = "Cant restart service \"launch on boot\"."

		user_pref = json.loads(self.user_manager.read_user_data())

		try:
			output = subprocess.run(["sudo", "systemctl", action, ON_BOOT_PROCESS_NAME], stdout=subprocess.PIPE)
			delete_folder_recursive(CACHE_FOLDER)
			print("\n"+success_msg+"\n")
			user_pref['on_boot_enabled'] = enabled_on_boot
			edit_file(USER_PREF_FILE, json.dumps(user_pref, indent=2), append=False)
			log.info(f"Start on boot created: \"{output.stdout.decode()}\"")
		except:
			print("\n"+fail_msg+"\n")
			log.critical("Something went wrong, could not enable \"start on boot\"")

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
		elif openvpn_PID and not (res.returncode == 0 and ("10.8.8.1" in res.stdout.decode() or "10.7.7.1" in res.stdout.decode())):
			print("VPN is running, but there might be DNS leaks. Try modifying your DNS configurations.")
			log.warning(f"Resolv conf has original values, custom ProtonVPN DNS configuration not found: {res.stdout.decode()}")
		else:
			print("VPN is not running.")
			log.info("Could not find any OpenVPN processes.")

	def check_for_running_ovpn_process(self):
		openvpn_PID = False
		command_list = [["pgrep", "openvpn"], ["pid", "openvpn"]]
		#no need to try, since cmd_command already does that
		try:
			for command in command_list:
				openvpn_PID = cmd_command(command)
				if openvpn_PID:
					return openvpn_PID
		except:
			log.warning(f"Could not find any openvpn processes running.")
			return openvpn_PID

	