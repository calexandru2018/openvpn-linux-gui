import os, subprocess

from include.server_manager import ServerManger
from include.user_manager import UserManager
from include.connection_manager import ConnectionManager

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		self.current_working_dir = os.getcwd()
		self.connMan = ConnectionManager(self.current_working_dir)
		self.switch()

	def switch(self):
		while True:
			self.choice = int(input("[MAIN MENU] What would you like to do: "))
			if(self.choice == 1):
				UserManager().createUser()
				continue
			elif(self.choice == 2):
				UserManager().editUser()
				continue
			elif(self.choice == 3):
				country = input("Which country to connect to: ")
				self.connMan.check_folder(country)
				continue
			elif(self.choice == 4):
				print(self.connMan.check_requirments())
				continue
			elif(self.choice == 5):
				self.connMan.check_if_profile_initialized()
				continue
			elif(self.choice == 6):
				self.connMan.openvpn_connect()
				continue
			elif(self.choice == 7):
				self.connMan.openvpn_disconnect()
				continue
			elif(self.choice == 8):
				ServerManger().collectServerList()
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
		print("\t[1] - Create user\n\t[2] - Edit User\n\t[3] - Serach server folder\n\t[4] - Check Requirments\n\t[5] - Network Manager\n\t[6] - OpenVPN Connect\n\t[7] - OpenVPN Disconnect\n\t[8] - Collect Server List\n\t[0] - Exit")
		print("---------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()