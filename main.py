import os, subprocess

from include.connection_manager import ConnectionManager
from include.check_requirments import (check_requirments)
from include.utils.constants import (USER_CRED_FILE)
from include.utils.connection_manager_helper import(generate_ovpn_file, manage_ipv6, manage_dns, manage_killswitch)

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
			elif(self.choice == 4):
				self.conn_manager.fastest_country()
				continue
			elif(self.choice == 5):
				self.conn_manager.openvpn_disconnect()
				continue
			elif(self.choice == 6):
				self.conn_manager.start_on_boot_manager("enable")
				continue
			elif(self.choice == 7):
				self.conn_manager.start_on_boot_manager("disable")
				continue
			elif(self.choice == 8):
				self.conn_manager.start_on_boot_manager("restart")
				continue
			elif(self.choice == 9):
				self.conn_manager.start_on_boot_manager("kill")
				continue
			elif(self.choice == 10):
				print("Quick connect to quickest server, country independent.")
				continue
			elif(self.choice == 11):
				self.conn_manager.fastest_feature("p2p")
				continue
			elif(self.choice == 12):
				self.conn_manager.fastest_feature("tor")
				continue
			elif(self.choice == 13):
				self.conn_manager.fastest_feature("secure core")
				continue
			elif(self.choice == 14):
				self.conn_manager.fastest_feature("Connect to last connected.")
				continue
			elif(self.choice == 15):
				choice = input("[C]ustom or [R]estore ? : ")
				restore_original_dns = "custom"

				if choice[0].lower() == "r":
					restore_original_dns = "restore" 

				manage_dns(action_type=restore_original_dns)
				continue
			elif(self.choice == 16):
				self.conn_manager.restart_network_manager()
				continue
			elif(self.choice == 17):
				choice = input("Disable IPV6 ? : ")
				action = "restore"

				if choice[0].lower() == "y":
					action = "disable"

				# manage_ipv6(disable_ipv6=disable_ipv6)
				manage_ipv6(action_type=action)
				continue
			elif(self.choice == 18):
				self.conn_manager.is_vpn_running()
				continue
			elif(self.choice == 99):
				choice = input("Enable killswitch ? : ")
				action = "restore"

				if choice[0].lower() == "y":
					action = "enable"

				# manage_ipv6(disable_ipv6=disable_ipv6)
				manage_killswitch(action)
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
	!!!!	            openvpn-linux-cli               !!!!
	!!!!                   Alpha v0.2.0                 !!!!
	!!!!                                                !!!! 
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	[1] - Check Requirments\t\t\t [9] - Kill "start on boot" process
	[2] - Create user\t\t\t [10] - Quick Connect [Under work]
	[3] - Edit User\t\t\t\t [11] - Connect to P2P [Under work]
	[4] - VPN Fastest by Country\t\t [12] - Connect to TOR [Under work] 
	[5] - Disconnect VPN \t\t\t [13] - Connect to Secure Core [Under work]
	[6] - Enable "start on boot" service \t [14] - Connect to last selected [Under work] 
	[7] - Disable "start on boot" service \t\t
	[8] - Restart "start on boot" service \t\t 


	[15] - Manage DNS
	[16] - Restart NetworkManager
	[17] - Manage IPV6
	[18] - Is VPN Running
	[99] - Test purpose

	[50] - End active VPN sessions [Not working]

	[0] - Exit
	""")
		print("--------------------------------------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()