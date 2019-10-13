import subprocess

class ConnectionManager():
	def __init__(self):
		print("In connection manager")

	# check if profile was created/initialized: check_if_profile_initialized()

#[ConnectionManager] - 
# Create a function that  
 	# check for ip: check_ip()

	# check if there is nternet connection: is_internet_working_normally()

	# check if openVpn is installed is_openvpn_installed()

	# connect to open_vpn: openvpn_connect()

	# disconnect from open_vpn: openvpn_disconnect()

	# check for update_resolv_conf

	# install update_resolv_conf: install_update_resolv_conf

	# manage IPV6: manage_ipv6()

	# modify DNS: modify_dns()

	# initialize CLI: init_cli()

	#check requirments: check_requirements()
		# check if openvpn is installed
		# check if python/version is installed
		# check for sysctl (identify why ?)
		# check for sha512_sum
		# check if update-resolv-conf is installed

	def check_if_openvpn_is_currently_running(self):
		'''Checks if OpenVPN is running.

		Returns
		-------
		Bool:
			True if PID is found, False otherwise.
		'''
		open_vpn_process = subprocess.check_output(["pgrep", "openvpn"])
		if open_vpn_process:
			return True
		return False
