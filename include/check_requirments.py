import requests, re

from include.user_manager import UserManager 

# Helper methods and constants 
from include.utils.methods import (
	cmd_command, walk_to_file, get_ip
)

def check_requirments():
	allReqCheck = 6
	checker = {
		'check_python_version': {'name': 'Python Version is above 3.3', 'return': check_python_version()},
		'is_internet_working_normally': {'name': 'Your internet is working normally', 'return': is_internet_working_normally()},
		'is_profile_initialized': {'name': 'Your profile is initialized', 'return': check_if_profile_initialized(requirments_check=True)},
		'is_openvpn_installed': {'name': 'OpenVPN is installed', 'return': is_openvpn_installed()}, 
		'is_open_resolv_installed': {'name': 'Open Resolv installed', 'return': is_open_resolv_installed('/etc/', 'resolv.conf')},
		'is_is_update_resolv_conf_installed': {'name': 'Update resolv is installed', 'return': is_update_resolv_conf_installed('/etc/openvpn/', 'update-resolv-conf')}
	}
	for check in checker:
		if not checker[check]['return']:
			allReqCheck -= allReqCheck
		print(f"{checker[check]['name']}: {checker[check]['return']}")
	return allReqCheck == 6

# check if profile was created/initialized: check_if_profile_initialized()
def check_if_profile_initialized(requirments_check=False):
	'''Checks if user profile is configured/intialized.

	Returns:
	------
	Bool:
		1 - Returns True if user already is configured/intialized.
		2 - Returns True if no user was found and a new one was configured/initialized.
		3 - Returns False if it was unable to configure/initialize a new user. 
	'''
	user_manager = UserManager()
	if user_manager.check_if_user_exist():
		#print("User exists")
		return True
	else:
		# if(requirments_check == False):
		# 	userChoice = input("User was not created, would you like to create it now ? [y/n]: ")
		# 	if(userChoice[0].lower() == 'y'):
		# 		if self.user_manager.create_server_conf() and self.user_manager.create_user_credentials():
		# 			print("User created succesfully!")
		# 			return True
		# 		print("Unable to create user")
		# 		return False
		# else:
		# 	return False
		return False

# check if there is internet connection: is_internet_working_normally()
def is_internet_working_normally():
	'''Checks if there is internet connection, by getting the IP.
	
	Returns:
	-------
	Bool:
		True if ther is internet connection, False otherwise.
	'''
	if get_ip():
		return True
	return False

# check if openVpn is installed is_openvpn_installed()
def is_openvpn_installed():
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

def check_if_openvpn_is_currently_running():
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

def check_python_version():
	pythonVersion = cmd_command(["python", "--version"])
	if pythonVersion and pythonVersion.split(' ')[1] > '3.3':
		return True
	return False

# check if openresolv is installed: is_open_resolv_installed()
def is_open_resolv_installed(path, fileName):
	return walk_to_file(path, fileName)

# check for update_resolv_conf()
def is_update_resolv_conf_installed(path, fileName):
	return walk_to_file(path, fileName)