import os, subprocess

from include.connection_manager import ConnectionManager

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		# user home folder
		self.rootDir = os.getcwd()
		self.user_man_folder_name = "user_conf"
		self.server_man_folder_name = "cache"
		# this in case run from home location
		#self.rootDir = self.rootDir+"/Python/protonvpn-linux-gui/"
		# this in case run from inside folder
		self.rootDir = self.rootDir
		self.connMan = ConnectionManager(self.rootDir, self.user_man_folder_name, self.server_man_folder_name)
		#print(self.rootDir)
		self.switch()

	def switch(self):
		while True:
			self.choice = int(input("[MAIN MENU] What would you like to do: "))
			if(self.choice == 1):
				self.connMan.check_requirments()
				continue
			elif(self.choice == 2):
				self.connMan.initialize_user_profile()
				continue
			elif(self.choice == 3):
				self.connMan.edit_user_profile()
				continue
			elif(self.choice == 4):
				self.connMan.cache_servers()
				continue
			elif(self.choice == 5):
				self.connMan.generate_ovpn_file()
				continue
			elif(self.choice == 6):
				self.connMan.openvpn_connect()
				continue
			elif(self.choice == 7):
				self.connMan.openvpn_disconnect()
				continue
			elif(self.choice == 8):
				#self.connMan.enable_vpn_on_boot()
				self.connMan.openvpn_service_manager("enable")
				continue
			elif(self.choice == 9):
				#self.connMan.enable_vpn_on_boot()
				self.connMan.openvpn_service_manager("disable")
				print("Disable start on boot")
				continue
			elif(self.choice == 10):
				self.connMan.modify_dns()
				continue
			elif(self.choice == 11):
				self.connMan.modify_dns(restore_original_dns=True)
				continue
			elif(self.choice == 12):
				#self.connMan.restart_on_boot_service()
				self.connMan.openvpn_service_manager("restart")
				continue
			elif(self.choice == 13):
				#self.connMan.restart_on_boot_service()
				self.connMan.restart_network_manager()
				continue
			elif(self.choice == 14):
				#self.connMan.restart_on_boot_service()
				choice = input("Disable IPV6 ? :")
				_choice_ = False
				if choice[0].lower() == "y":
					_choice_ = True
				elif choice[0].lower() == "n":
					_choice_ == False 
				self.connMan.manage_ipv6(disable_ipv6=_choice_)
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
	!!!!	        ProtonVPN Unofficial CLI            !!!!
	!!!!                   Alpha v.1                    !!!!
	!!!!                                                !!!! 
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	[1] - Check Requirments\t\t [8] - Enable "start on boot" service
	[2] - Create user\t\t [9] - Disable "start on boot" service
	[3] - Edit User\t\t\t [10] - Modify DNS (OVPN should fix it automatically)
	[4] - Cache Servers\t\t [11] - Restore original DNS
	[5] - Generate OPVN file\t [12] - Restart "start on boot" service
	[6] - OpenVPN Connect\t\t [13] - Restart NetworkManager
	[7] - OpenVPN Disconnect\t [14] - Manage IPV6[Work in progress]
		
			
	[0] - Exit""")
		print("--------------------------------------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()