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

def auto_select_optimal_server(data, tier):
	"""Returns a tuple with information abou the most optimal server.
	
	data: information about server of a specific country
	tier: the actual user tier

	
	Returns: tuple (connection_ID, best_score, server_name, server_load) 
	-------
	"""
	best_score = 999
	connection_ID = ''
	server_name = ''

	for server in data['serverList']:
		if (data['serverList'][server]['score'] < best_score) and (int(data['serverList'][server]['tier']) == tier):
			server_name = data['serverList'][server]['name']
			connection_ID = data['serverList'][server]['id']
			best_score = data['serverList'][server]['score']
			server_load = data['serverList'][server]['load']

	connectInfo = (connection_ID, best_score, server_name, server_load)
	log.debug(f"Connection information {connectInfo}")
	return connectInfo


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

def generate_ovpn_file(server_list, server_req):
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
		cmd = False

		log.info("Applying custom ProtonVPN DNS...")

		try: 
			shutil.copy(resolv_conf_path, RESOLV_BACKUP_FILE)
			cmd = "cat > /etc/resolv.conf <<EOF "+PROTON_DNS+"\nEOF"
		except :
			print("Unable to backup DNS configurations.")
			log.warning("Unable to backup DNS configurations.")
			return False

		try:
			subprocess.run(["sudo", "bash", "-c", cmd])
			print("DNS updated with new configurations.")
			log.info("...custom ProtonVPN DNS applied.")
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


# manage IPV6: manage_ipv6()
def manage_ipv6(disable_ipv6):
	ipv6 = False
	netmask = False
	ipv6_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=1"]
	ipv6_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=1"]

	if not disable_ipv6:
		log.info("Start IPV6 restore process.")
		
		try:
			with open(IPV6_BACKUP_FILE, "r") as file:
				content = file.read().split()
		except:
			return False

		ipv6_default = ["sysctl", "-w", "net.ipv6.conf.default.disable_ipv6=0"]
		ipv6_all = ["sysctl", "-w", "net.ipv6.conf.all.disable_ipv6=0"]
		
		if (not cmd_command(ipv6_default, as_sudo=True)) or (not cmd_command(ipv6_all, as_sudo=True)):
			print("Did not manage to restore IPV6, needs to be restored manually.")
			log.warning("Could not restore IPV6.")
			return False

		if not cmd_command(["ip", "addr", "add", content[1] , "dev", content[0]],  as_sudo=True):
			return False

		log.info("IPV6 Restored and linklocal restored.")
		print("IPV6 Restored and linklocal restored.")

		if not delete_file(IPV6_BACKUP_FILE):
			log.warning(f"Could not delete IPV6 backup file at: \"{IPV6_BACKUP_FILE}\"")
		
		log.info("IPV6 backup file was deleted.")
		
		return True

	else:
		log.info("Start IPV6 disable process.")
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
						log.info(f"IPV6 found: \"{ipv6}\"")
						break

		if not ipv6 and not netmask:
			log.critical("Could not find IPV6 and netmask.")
			return False
		
		if walk_to_file(USER_FOLDER, IPV6_BACKUP_FILE.split("/")[-1]):	
			delete_file(IPV6_BACKUP_FILE)
			log.info(f"Backup file was deleted: \"{IPV6_BACKUP_FILE}\"")
		
		#try except
		with open(IPV6_BACKUP_FILE, "w") as file:
			file.write(interface_to_save + " " + ipv6 + netmask)

		if (not cmd_command(ipv6_default, as_sudo=True)) or (not cmd_command(ipv6_all, as_sudo=True)):
			log.critical("Unable to run CMD commands to disable IPV6.")
			return False

		print("IPV6 disabled.")
		log.info("...IPV6 was disabled successfully.")
		return True

def generate_ovpn_for_boot(user_data):
	country = input("Which country to connect to: ")
	file = country.upper() + SERVER_FILE_TYPE

	if not walk_to_file(CACHE_FOLDER, file):
		print("There is no such file, maybe servers are not cached ?")
		log.warning("Server files not found, maybe not cached.")
		return False

	try:
		with open(os.path.join(CACHE_FOLDER, file)) as file:
			data = json.load(file)
	except:
		log.warning("Could not find cached server.")
		return False

	connectionID, best_score, server_name, server_load = auto_select_optimal_server(data, user_data['tier'])

	user_data['on_boot_enabled'] = False
	user_data['on_boot_server_id'] = connectionID
	user_data['on_boot_server_name'] = server_name
	user_data['on_boot_protocol'] = user_data['protocol']

	url = "https://api.protonmail.ch/vpn/config?Platform=" + OS_PLATFORM + "&LogicalID="+connectionID+"&Protocol=" + user_data['protocol']
	try:
		server_req = requests.get(url, headers=(PROTON_HEADERS))
		log.info("Fetched request from ProtonVPN.")
	except:
		log.critical("Unable to fetch request from ProtonVPN.")
		return False
	original_req = server_req.text
	start_index = original_req.find("auth-user-pass")
	modified_request = original_req[:start_index+14] + " /opt/" + PROJECT_NAME + "/" + USER_CRED_FILE.split("/")[-1] + original_req[start_index+14:]
	ovpn_file_created = False
	#append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"
	append_to_file = "cat > /etc/openvpn/client/"+OVPN_FILE.split("/")[-1].split(".")[0]+".conf <<EOF "+modified_request+"\nEOF"

	try:
		subprocess.run(["sudo", "bash", "-c", append_to_file])
		print("Created new file in /openvpn/client/")
		log.info(f"\"Start on boot\" path to credentials injected.")
		ovpn_file_created = True
	except:
		print("Unable to create configuration file in /openvpn/client/")
		log.critical(f"Could not generate/modify openVPN file.")

	if ovpn_file_created and walk_to_file("/opt/", USER_CRED_FILE, in_dirs=True):
		log.critical(f"OVPN file for boot was NOT generated in: \"/etc/openvpn/client/\"")
		return False
	
	if not copy_credentials():
		return False
	
	if not edit_file(USER_PREF_FILE, json.dumps(user_data, indent=2), append=False):
		return False

	filename = OVPN_FILE.split("/")[-1].split(".")[0]
	log.info(f"OVPN file for boot was generated: \"/etc/openvpn/client/{filename}\"")
	return True

def copy_credentials():
	cmds = ["mkdir /opt/"+PROJECT_NAME+"/", "cp " +USER_CRED_FILE+" /opt/"+PROJECT_NAME+"/"]
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
		log.critical(f"Unable to copye credentials to: \"/opt/{PROJECT_NAME}\"")
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