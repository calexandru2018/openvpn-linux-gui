import os, subprocess

from include.server_manager import ServerManger
from include.user_manager import UserManager
from include.connection_manager import ConnectionManager

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		self.rootDir = os.getcwd()
		self.connMan = ConnectionManager(self.rootDir)
		self.switch()

	def switch(self):
		while True:
			self.choice = int(input("[MAIN MENU] What would you like to do: "))
			if(self.choice == 1):
				print(self.connMan.check_requirments())
				continue
			elif(self.choice == 2):
				UserManager(self.rootDir).createUser()
				continue
			elif(self.choice == 3):
				UserManager(self.rootDir).editUser()
				continue
			elif(self.choice == 4):
				ServerManger(self.rootDir).collectServerList()
				continue
			elif(self.choice == 5):
				country = input("Which country to connect to: ")
				self.connMan.generate_ovpn_file(country)
				continue
			elif(self.choice == 6):
				self.connMan.openvpn_connect()
				continue
			elif(self.choice == 7):
				self.connMan.openvpn_disconnect()
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
		print("\t[1] - Check Requirments\n\t[2] - Create user\n\t[3] - Edit User\n\t[4] - Cache Servers\n\t[5] - Generate OPVN file\n\t[6] - OpenVPN Connect\n\t[7] - OpenVPN Disconnect\n\t[8] - Collect Server List\n\t[0] - Exit")
		print("---------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()