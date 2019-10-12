import os, subprocess

from include.server_manager import ServerManger
from include.user_manager import UserManager

# app main class
class AppEntry():
	def __init__(self):
		self.showMenu()
		self.switch()

	def switch(self):
		while True:
			self.choice = int(input("[MAIN MENU] What would you like to do: "))
			if(self.choice == 1):
				UserManager().createUser()
				continue
			elif(self.choice == 2):
				UserManager().editUser()
				UserManager().editUser()
				continue
			elif(self.choice == 3):
				ServerManger()
				continue
			elif(self.choice == 4):
				print(os.fspath(os.getcwd()))
				print(os.getlogin())
				print("usertype: ",os.getuid())
				print(os.uname())
				subprocess.run(["which", "openvpn"])
				subprocess.run(["pgrep", "openvpn"])
				break
			elif(self.choice == 0):
				print("Exit program\n")
				break
			else:
				print("Wrong answer")
				continue
			self.showMenu()

	def showMenu(self):
		print("---------------------------------------------------------")
		print("\t[1] - Create user\n\t[2] - Edit User\n\t[3] - Generate server files\n\t[4] - Check OPENVPN\n\t[0] - Exit")
		print("---------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()