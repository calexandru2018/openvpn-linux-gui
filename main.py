from include.server_manager import ServerManger
from include.user_manager import UserManager

#app main class
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
				continue
			elif(self.choice == 3):
				ServerManger()
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
		print("\t[01] - Create user\n\t[02] - Edit User\n\t[03] - Generate server files")
		print("---------------------------------------------------------")

if __name__ == '__main__':
	AppEntry()