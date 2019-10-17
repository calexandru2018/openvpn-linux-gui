import os, subprocess

from include.connection_manager import ConnectionManager

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		# user home folder
		self.rootDir = os.getcwd()
		self.user_man_folder_name = "protonvpn_conf"
		self.server_man_folder_name = "servers_in_cache"
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
				self.connMan.start_on_boot()
				continue
			elif(self.choice == 9):
				self.connMan.modify_dns()
				continue
			elif(self.choice == 99):
				self.connMan.modify_dns(restore_original_dns=True)
				continue
			elif(self.choice == 0):
				print("Exit program\n")
				break
			else:
				print("Wrong answer")
				continue
			self.showMenu()

	def showMenu(self):
		print("---------------------------------------------------------")
		print("\t[1] - Check Requirments\n\t[2] - Create user\n\t[3] - Edit User\n\t[4] - Cache Servers\n\t[5] - Generate OPVN file\n\t[6] - OpenVPN Connect\n\t[7] - OpenVPN Disconnect\n\t[8] - Start on boot\n\t[9] - Modify DNS\n\t[99] - Restore original DNS\n\t[0] - Exit")
		print("---------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()