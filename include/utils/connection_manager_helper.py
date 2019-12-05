import os, json, netifaces, re, requests, shutil, subprocess

# Helper methods and constants 
from include.utils.common_methods import (
	walk_to_file, create_file, delete_file, delete_folder_recursive,
	cmd_command, edit_file
)
from include.utils.constants import (
	USER_CRED_FILE, USER_PREF_FILE, OVPN_FILE, CACHE_FOLDER, RESOLV_BACKUP_FILE, IPV6_BACKUP_FILE, SERVER_FILE_TYPE, 
	OS_PLATFORM, USER_FOLDER, PROTON_HEADERS, PROJECT_NAME, PROTON_DNS, ON_BOOT_PROCESS_NAME,PROTON_CHECK_URL
)

from include.logger import log

def get_fastest_server(server_list):
	"""
	Returns the fastest server from the list.
	"""

	fastest_server = sorted(server_list, key=lambda server: server["score"])
	log.debug(f"Connection information {fastest_server}")
	return (fastest_server[0]['id'], fastest_server[0]['score'], fastest_server[0]['name'], fastest_server[0]['load'])

def req_for_ovpn_file(server_id, user_protocol):
	"""
	Makes a request to ProtonVPN servers and returns with a OVPN template "file", returns False otherwise.
	"""

	url = f"https://api.protonmail.ch/vpn/config?Platform={OS_PLATFORM}&LogicalID={server_id}&Protocol={user_protocol}"

	try:
		log.info("Fetched request from ProtonVPN.")
		return requests.get(url, headers=(PROTON_HEADERS))
	except:
		log.critical("Unable to fetch request from ProtonVPN.")
		return False

def generate_ovpn_file(server_req):
		'''Generates OVPN files
		
		Tier 0(1) = Free

		Tier 1(2) = Basic

		Tier 2(3) = Plus

		Tier 3(4) = Visionary
		----------
		Feature 1: Secure Core

		Feature 2: Tor

		Feature 4: P2P

		Feature 8: XOR (not in use)

		Feature 16: IPV6 (not in use)
		'''

		if not server_req:
			return False

		if walk_to_file(USER_FOLDER, OVPN_FILE.split("/")[-1]):
			delete_file(OVPN_FILE)

		if not create_file(OVPN_FILE, server_req.text):
			log.warning("Unable to create ovpn file for direct connection.")
			return False

		print("An ovpn file has bee created, try to establish a connection now.")
		return True

def generate_ovpn_for_boot(server_req):

	original_req = server_req.text
	start_index = original_req.find("auth-user-pass")
	modified_request = original_req[:start_index+14] + " /opt/" + PROJECT_NAME + "/" + USER_CRED_FILE.split("/")[-1] + original_req[start_index+14:]
	ovpn_file_created = False
	append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split("/")[-1].split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"

	try:
		output = subprocess.run(["sudo", "bash", "-c", append_to_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		log.debug(f"Injection comand output: {output}")
		ovpn_file_created = True
	except:
		print("Unable to create configuration file in /openvpn/client/")
		log.critical(f"Could not generate/modify openVPN file.")
		return False

	print("Created new file in /openvpn/client/")
	log.info(f"\"Start on boot\" path to credentials injected.")

	if ovpn_file_created and walk_to_file("/opt/", USER_CRED_FILE, in_dirs=True):
		log.critical(f"OVPN file for boot was NOT generated in: \"/etc/openvpn/client/\"")
		return False
	
	if not copy_credentials():
		return False

	filename = OVPN_FILE.split("/")[-1].split(".")[0]
	log.info(f"OVPN file for boot was generated: \"/etc/openvpn/client/{filename}\"")
	return True

# modify DNS: modify_dns()
def modify_dns(restore_original_dns=False):
	resolv_conf_path = walk_to_file("/etc/", "resolv.conf", is_return_bool=False)
	
	if not resolv_conf_path:
		print("The \"resolv.conf\" file was not found on your system.")
		log.warning("\"resolv.conf\" file was not found.")
		return False

	log.info(f"Path to original resolv.conf: \"{resolv_conf_path}\"")
	print("Modifying dns...")

	if not restore_original_dns:
		log.info("Applying custom ProtonVPN DNS...")
		cmd = "cat > /etc/resolv.conf <<EOF "+PROTON_DNS+"\nEOF"

		try: 
			shutil.copy(resolv_conf_path, RESOLV_BACKUP_FILE)
		except:
			print("Unable to backup DNS configurations.")
			log.warning("Unable to backup DNS configurations.")
			return False

		try:
			output = subprocess.run(["sudo", "bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			print("DNS updated with new configurations.")
			log.debug(f"...custom ProtonVPN DNS applied: {output}")
			return True
		except:
			print("Unable to update DNS configurations")
			log.warning("Unable to apply custom ProtonVPN DNS configurations.")
			return False
	else:
		log.info("Restoring original DNS...")
		try:
			with open(RESOLV_BACKUP_FILE) as f:
				content = f.read()
			cmd = "cat > /etc/resolv.conf <<EOF \n"+content+"\nEOF"
			subprocess.run(["sudo", "bash", "-c", cmd])
			print("...DNS configurations were restored.")
			delete_file(RESOLV_BACKUP_FILE)
			log.info(f"Original configurations restored from: \"{RESOLV_BACKUP_FILE}\"")
			return True
		except:
			print("Unable to restore original DNS configurations, try restarting the Network Manager.")
			log.warning("Unable to restore original DNS configurations.")
			return False

def manage_ipv6(action_type):
		if action_type == "disable":
			#check for error
			default_route = subprocess.run("ip route show | grep default", shell=True, stdout=subprocess.PIPE)
			if not default_route.returncode == 0:
				print("Could not find any IPv6 configurations.")
				log.debug("Could not find any IPv6 configurations prior to disabling it.")
				return False
			# show all ipv6 interfaces and their status
			#all_interfaces = subprocess.run(["sudo sysctl --all | grep disable_ipv6"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

			default_nic = default_route.stdout.decode().strip().split()[4]
			
			ipv6_info = subprocess.run(f"ip addr show dev {default_nic} | grep '\<inet6.*global\>'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if not ipv6_info.returncode == 0:
				log.debug(f"Could not find ipv6 {ipv6_info}")
				return False

			ipv6_addr = ipv6_info.stdout.decode().strip().split()[1]

			if walk_to_file(USER_FOLDER, IPV6_BACKUP_FILE.split("/")[-1]):	
				delete_file(IPV6_BACKUP_FILE)
				log.info(f"Backup file was deleted: \"{IPV6_BACKUP_FILE}\"")
			
			ipv6_disable = subprocess.run(f"sudo sysctl -w net.ipv6.conf.{default_nic}.disable_ipv6=1", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			if not ipv6_disable.returncode == 0:
				log.debug(f"Unable to disable ipv6: {ipv6_disable}")
				return False

			try:
				with open(IPV6_BACKUP_FILE, "w") as file:
					file.write(default_nic + " " + ipv6_addr)
			except:
				print("Unable to save to file")
				return False
			print("Backup was made")
			return True

		elif action_type == "restore":
			log.info("Start IPV6 restore process.")
		
			try:
				with open(IPV6_BACKUP_FILE, "r") as file:
					content = file.read().split()
					default_nic = content[0].strip()
					ipv6_addr = content[1].strip()
			except:
				log.debug("Unable to open file.")
				return False

			ipv6_info = subprocess.run(f"ip addr show dev {default_nic} | grep '\<inet6.*global\>'", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

			if ipv6_info.returncode == 0:
				log.debug("IPv6 already present.")
				delete_file(IPV6_BACKUP_FILE)
				return True

			ipv6_enable = subprocess.run(f"sudo sysctl -w net.ipv6.conf.{default_nic}.disable_ipv6=0", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

			if not ipv6_enable.returncode == 0:
				print("Unable to restore IPv6 configurations, restarting Network Manager might help.")
				log.debug(f"IPv6 configuration restoration error: {ipv6_enable}")
				return False

			ipv6_restore_address = subprocess.run(f"sudo ip addr add {ipv6_addr} dev {default_nic}", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

			if not ipv6_restore_address.returncode == 0:
				print("Unable to restore IPv6.")
				log.debug(f"IPv6 restoration error: {ipv6_restore_address}")
				return False

			log.debug("Removing IPv6 backup file.")
			delete_file(IPV6_BACKUP_FILE)
			log.debug("IPv6 restored")
			print("IPv6 restored")

			return True
			

def copy_credentials():
	cmds = [f"mkdir /opt/{PROJECT_NAME}/", f"cp {USER_CRED_FILE} /opt/{PROJECT_NAME}/"]
	try:
		if(not os.path.isdir("/opt/"+PROJECT_NAME+"/")):
			for cmd in cmds:
				subprocess.run(["sudo", "bash", "-c", cmd])
		else:
			subprocess.run(["sudo", "bash", "-c", cmds[1]])

		print("Copied credentials")
		log.info(f"Credentials were copied to: \"/opt/{PROJECT_NAME}\"")
		return True
	except:
		print("Unable to copy credentials")
		log.critical(f"Unable to copy credentials to: \"/opt/{PROJECT_NAME}\"")
		return False

# check for ip: get_ip_info()
def get_ip_info():
	'''Gets the host IP from two different sources and compares them.
	
	Returns:
	-------
	Bool:
		True if the IP's match, False otherwise.
	'''
	protonRequest = False

	protonRequest = requests.get(PROTON_CHECK_URL, headers=(PROTON_HEADERS)).json()

	if not protonRequest:
		return False
	#print("Internet is OK and your IP is:", dyndnsIp)
	return (protonRequest['IP'], protonRequest['ISP'])