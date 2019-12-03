import os, subprocess

from include.connection_manager import ConnectionManager
from include.check_requirments import (check_requirments)
from include.utils.constants import (USER_CRED_FILE)
from include.utils.connection_manager_helper import(generate_ovpn_file, modify_dns, manage_ipv6)

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		self.conn_manager = ConnectionManager()
		self.switch()

	def switch(self):
		while True:
			self.choice = int(input("[MAIN MENU] What would you like to do: "))
			if(self.choice == 1):
				check_requirments()
				continue
			elif(self.choice == 2):
				self.conn_manager.initialize_user_profile()
				continue
			elif(self.choice == 3):
				self.conn_manager.edit_user_profile()
				continue
			# elif(self.choice == 4):
			# 	self.conn_manager.cache_servers()
			# 	continue
			# elif(self.choice == 5):
			# 	generate_ovpn_file()
			# 	continue
			elif(self.choice == 6):
				self.conn_manager.fastest_country()
				continue
			elif(self.choice == 7):
				self.conn_manager.openvpn_disconnect()
				continue
			elif(self.choice == 8):
				self.conn_manager.start_on_boot_manager("enable")
				continue
			elif(self.choice == 9):
				self.conn_manager.start_on_boot_manager("disable")
				continue
			elif(self.choice == 10):
				print("Start/stop on boot service")
				continue
			elif(self.choice == 11):
				self.conn_manager.start_on_boot_manager("restart")
				continue
			elif(self.choice == 12):
				choice = input("[C]ustom or [R]estore ? : ")
				restore_original_dns = False

				if choice[0].lower() == "r":
					restore_original_dns = True 

				modify_dns(restore_original_dns=restore_original_dns)
				continue
			elif(self.choice == 13):
				self.conn_manager.restart_network_manager()
				continue
			elif(self.choice == 14):
				choice = input("Disable IPV6 ? : ")
				disable_ipv6 = False

				if choice[0].lower() == "y":
					disable_ipv6 = True

				manage_ipv6(disable_ipv6=disable_ipv6)
				continue
			elif(self.choice == 15):
				print("Test things")
				continue
			elif(self.choice == 20):
				self.conn_manager.connect_to_p2p()
				continue
			elif(self.choice == 21):
				self.conn_manager.connect_to_tor()
				continue
			elif(self.choice == 22):
				self.conn_manager.connect_to_secure_core()
				continue
			elif(self.choice == 23):
				self.conn_manager.is_vpn_running()
				continue
			elif(self.choice == 0):
				print("Exit program\n")
				break
			else:
				print("Wrong choice, try again.")
				continue
			self.showMenu()

	def showMenu(self):
		print("--------------------------------------------------------------------------------------")
		print("""
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	!!!!                                                !!!!   
	!!!!	       Made by Alexandru Cheltuitor         !!!!
	!!!!                                                !!!!
	!!!!	            openvpn-linux-cli               !!!!
	!!!!                   Alpha v0.1.0                 !!!!
	!!!!                                                !!!! 
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	[1] - Check Requirments\t\t [8] - Enable "start on boot" service
	[2] - Create user\t\t [9] - Disable "start on boot" service
	[3] - Edit User\t\t\t [10] - Start/Stop "start on boot" service
	[4] - Cache Servers\t\t [11] - Restart "start on boot" service
	[5] - Generate OPVN file\t [12] - Manage DNS
	[6] - OpenVPN Connect\t\t [13] - Restart NetworkManager
	[7] - OpenVPN Disconnect\t [14] - Manage IPV6


	[15] - End active VPN sessions\t\t [23] - Is VPN Running
	[16] - Check DNS\t\t
	[17] - Quick Connect\t\t
	[18] - Connect to last selected\t\t
	[19] - Connect to quickest[country]\t\t
	[20] - Connect to P2P\t\t
	[21] - Connect to TOR\t\t
	[22] - Connect to Secure Core\t\t


	[0] - Exit
	""")
		print("--------------------------------------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()