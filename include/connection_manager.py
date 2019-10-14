import subprocess, requests, re, os
from include.user_manager import UserManager

class ConnectionManager():
	def __init__(self):
		print("\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n\t! In connection manager !\n\t!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		self.ipDyndnsCheckUrl = "http://checkip.dyndns.org"
		self.ipProtonCheckUrl = "https://api.protonmail.ch/vpn/location"
		self.user = UserManager()
		self.is_openvpn_installed()
		self.check_if_openvpn_is_currently_running()
		self.check_python_version()
		self.check_ip()
		self.is_open_resolv_installed('/etc/', 'resolv.conf')
		self.update_resolv_conf_installed('/etc/openvpn/', 'update-resolv-conf')
		self.openvpn_connect()

	# check if profile was created/initialized: check_if_profile_initialized()
	def check_if_profile_initialized(self):
		'''Checks if user profile is configured/intialized.

		Returns:
		------
		Bool:
			1 - Returns True if user already is configured/intialized.
			2 - Returns True if no user was found and a new one was configured/initialized.
			3 - Returns False if it was unable to configure/initialize a new user. 
		'''
		if self.user.checkUserExists():
			print("User exists")
			return True
		else:
			userChoice = input("User was not created, would you like to create it now ? [y/n]: ")
			if(userChoice[0].lower() == 'y'):
				if self.user.createUser():
					print("User created succesfully!")
					return True
				print("Unable to create user")
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
			print("Internet is OK and your IP is:", dyndnsIp)
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
			print("Is OpenVPN installed: ", decodedString)
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
		print("Is OpenVPN running: ", open_vpn_process)
		if open_vpn_process:
			return True
		return False

	def check_python_version(self):
		pythonVersion = self.cmdCommand(["python", "--version"])
		if pythonVersion.split(' ')[1] > '3.3':
			print("Your Python version: ", pythonVersion)
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
		subprocess.Popen(["openvpn", "--config", "/etc/openvpn/server.opvn"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
		# use sudo systemctl enable openvpn-client@server.service; server is the filename and it should en in .conf

	# disconnect from open_vpn: openvpn_disconnect()

	

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
				print(file, os.path.join(root, file))
				return True
		return False
